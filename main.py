from schnorr import SchnorrZKP
from voting import Ciudadano, Voto, ElectionAuthority, Election


def main():

    print("Elecciones presidenciales 2026")

    schnorr = SchnorrZKP()
    authority = ElectionAuthority()
    election = Election()

    # Base de datos local de ciudadanos
    ciudadanos = {}

    print("\nRegistrando ciudadanos...\n")

    cedulas = [
        "100000001",
        "100000002",
        "100000003"
    ]

    for cedula in cedulas:

        private_key, public_key = schnorr.generate_keypair()

        ciudadano = Ciudadano(
            cedula=cedula,
            private_key=private_key,
            public_key=public_key
        )

        ciudadanos[cedula] = ciudadano

        authority.register(ciudadano)

        print(f"Ciudadano {cedula} registrado.")

    while True:
        cedula = input("Ingrese la cédula (0 para terminar): ")

        if cedula == "0":
            break

        if not authority.can_vote(cedula):
            print("La cédula no existe o ya votó.")
            continue

        ciudadano = ciudadanos[cedula]

        print("\nAutenticando identidad mediante Schnorr...")

        r, commitment = ciudadano.create_commitment(schnorr)

        challenge = schnorr.create_challenge()

        response = ciudadano.create_response(
            schnorr,
            r,
            challenge
        )

        authenticated = authority.authenticate(
            schnorr,
            cedula,
            commitment,
            challenge,
            response
        )

        if not authenticated:
            print("\nAutenticación fallida.")
            continue

        print("\nAutenticación exitosa.")

        # Mostrar candidatos
        election.show_candidates()

        try:

            candidate = int(
                input("\nSeleccione un candidato: ")
            )

            vote_vector = election.build_vote_vector(candidate)

        except Exception:

            print("\nCandidato inválido.")

            continue

        election.register_vote(vote_vector)

        authority.mark_as_voted(cedula)

        print("\nVoto registrado correctamente.")
        print(f"Vector almacenado: {vote_vector}")

    election.close_election()

    print()


if __name__ == "__main__":
    main()