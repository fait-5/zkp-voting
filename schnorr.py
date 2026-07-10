import hashlib
import secrets
from Crypto.PublicKey import DSA

class SchnorrZKP:

    def __init__(self):

        self.p = 28353395476157704529633964138011736381112095252362710416386886652088599267878750888454709821803015664158192544161321084079532418955266164635488070999764151398132973199470723757524045208383543366620362471436320827800927354356187098199853331044784461325384105808191243834001278214237325201456738203374295250781490135294114873305144215026928109903737074660197116847337345461205019139906803053689558500217479965585220509305287342552054145708719154206241434272663383518523033562228054851169229047955543573990169505672752479354224615905866045695759568430970074830483724344817168601173448908829645230084117661244733841580277
        self.q = 26632289007672472919209512279054738982973014773399053374876398249689
        self.g = 26322575663532369269842142763857356045657812096416788994389913644132498696134971525942909659246405841781408908860521539546141585994362384449405715394903731590056530384989991995599560002515399131556828957543212611743025143756354897671229832333429360070560106228403646367687636567859614662379464557412610363937429596337093384053394659596827364871318113644622316951988822193084324850716176754638693033076547009651721866660469732476411124580922545424429593266363057845547878774657511037050476410356338596008209900946507960813456874540320681766209939776652968411755680449161982516536293835398587244104680102686195924001319

    # Generación de claves

    def generate_keypair(self):
        x = secrets.randbelow(self.q - 1) + 1

        y = pow(self.g, x, self.p)

        return x, y

    def create_commitment(self):
        # t = g^r mod p
        r = secrets.randbelow(self.q - 1) + 1
        t = pow(self.g, r, self.p)
        return r, t

    def create_challenge(self):
        return secrets.randbelow(self.q - 1) + 1

    def create_response(self, private_key, r, challenge):
        s = (r + challenge * private_key) % self.q
        return s

    def verify(self, public_key, commitment, challenge, response):  
        left = pow(self.g, response, self.p)
        right = (
            commitment *
            pow(public_key, challenge, self.p)
        ) % self.p

        return left == right

if __name__ == "__main__":
    schnorr = SchnorrZKP()

    print("Generando claves")

    private_key, public_key = schnorr.generate_keypair()

    print(f"Clave privada: {private_key}")
    print(f"Clave pública: {public_key}")
    print()
    print("Inicio del protocolo")

    r, commitment = schnorr.create_commitment()

    print(f"Compromiso enviado: {commitment}")
    challenge = schnorr.create_challenge()

    print(f"Desafío del servidor: {challenge}")
    response = schnorr.create_response(
        private_key,
        r,
        challenge
    )
    print(f"Respuesta enviada: {response}")

    valid = schnorr.verify(
        public_key,
        commitment,
        challenge,
        response
    )

    print()

    if valid:
        print("Prueba válida")
    else:
        print("Prueba inválida")