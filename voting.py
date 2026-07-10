import json
import hashlib
from dataclasses import dataclass
from secrets import token_bytes
from Crypto.Cipher import AES

@dataclass
class Ciudadano:
    cedula: str
    private_key: int
    public_key: int

    def create_commitment(self, schnorr):
        return schnorr.create_commitment()
    
    def create_response(self, schnorr, r, challenge):
        return schnorr.create_response(self.private_key, r, challenge)

@dataclass
class RegisteredCitizen:
    cedula_hash: str
    public_key: int

@dataclass
class Voto:
    ciphertext: bytes
    nonce: bytes
    tag: bytes

class ElectionAuthority:

    def __init__(self):
        self.registered = {}
        self.already_voted = set()

    def register(self, ciudadano):
        self.registered[self.hash_id(ciudadano.cedula)] = RegisteredCitizen(
            cedula_hash=self.hash_id(ciudadano.cedula),
            public_key=ciudadano.public_key
        )

    def get(self, cedula: str):
        return self.registered.get(self.hash_id(cedula))

    def hash_id(self, cedula):
        return hashlib.sha256(cedula.encode()).hexdigest()

    def has_voted(self, cedula):
        return self.hash_id(cedula) in self.already_voted

    def can_vote(self, cedula: str):
        return (
            self.hash_id(cedula) in self.registered
            and
            self.hash_id(cedula) not in self.already_voted
        )

    def mark_as_voted(self, cedula):
        self.already_voted.add(self.hash_id(cedula))

    def authenticate(self, schnorr, cedula, commitment, challenge, response):
        ciudadano = self.get(cedula)

        if ciudadano is None:
            return False

        return schnorr.verify(
            ciudadano.public_key,
            commitment,
            challenge,
            response
        )

class Election:

    def __init__(self):
        self.candidates = [
            "Baal",
            "Moloch"
        ]
        self.votes = []
        # Clave AES
        self.aes_key = token_bytes(32)

    def show_candidates(self):
        print("\nCandidatos:\n")
        for i, candidate in enumerate(self.candidates, start=1):
            print(f"{i}. {candidate}")

    def build_vote_vector(self, candidate: int):
        if candidate < 1 or candidate > len(self.candidates):
            raise ValueError("Candidato inválido.")

        vector = [0] * len(self.candidates)
        vector[candidate - 1] = 1
        return vector

    def register_vote(self, vote_vector):
        plaintext = json.dumps(vote_vector).encode()

        cipher = AES.new(
            self.aes_key,
            AES.MODE_GCM
        )

        ciphertext, tag = cipher.encrypt_and_digest(
            plaintext
        )

        vote = Voto(
            ciphertext=ciphertext,
            nonce=cipher.nonce,
            tag=tag
        )

        self.votes.append(vote)

    def count_votes(self):
        results = [0] * len(self.candidates)
        for vote in self.votes:
            for i, value in enumerate(vote.vote_vector):
                results[i] += value

        return results

    def show_results(self):
        print("\nResultados:\n")
        results = self.count_votes()
        for candidate, votes in zip(self.candidates, results):
            print(f"{candidate}: {votes}")

    def close_election(self):
        print("\nCerrando la elección...\n")
        results = [0] * len(self.candidates)
        for vote in self.votes:
            cipher = AES.new(
                self.aes_key,
                AES.MODE_GCM,
                nonce=vote.nonce
            )

            plaintext = cipher.decrypt_and_verify(
                vote.ciphertext,
                vote.tag
            )

            vector = json.loads(
                plaintext.decode()
            )

            for i, value in enumerate(vector):
                results[i] += value

        print("\nResultados finales:\n")

        for candidate, total in zip(self.candidates, results):
            print(f"{candidate}: {total}")