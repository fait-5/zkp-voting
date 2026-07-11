# ZKP Voting

## Sistema de votación electrónica con pruebas de conocimiento cero

**ZKP Voting** es una prueba de concepto académica para un sistema de votación electrónica que combina identificación ciudadana, prevención de votos repetidos, cifrado autenticado y pruebas de conocimiento cero.

El sistema busca garantizar cuatro propiedades principales:

1. **Elegibilidad:** solamente pueden votar ciudadanos previamente registrados.
2. **Unicidad:** cada ciudadano puede emitir como máximo un voto por elección.
3. **Privacidad:** el voto permanece cifrado y no se almacena junto con la identidad del votante.
4. **Validez verificable:** el sistema debe poder comprobar que una papeleta contiene exactamente una selección válida sin revelar el candidato elegido.

---

## Problema

Un sistema electoral debe cumplir dos requisitos que parecen contradictorios:

- La autoridad necesita identificar al ciudadano para comprobar que está registrado y evitar que vote más de una vez.
- La urna no debería conocer ni almacenar por quién votó esa persona.

Una implementación como la siguiente sería problemática:

```text
cédula -> voto cifrado
```

Aunque el voto esté cifrado, seguiría existiendo una relación directa entre la identidad y la papeleta. Si la clave de descifrado se filtra posteriormente, sería posible conocer el voto de cada ciudadano.

La arquitectura propuesta separa ambos registros:

```text
Autoridad electoral:
hash(cédula) -> ya votó

Urna electrónica:
identificador aleatorio -> voto cifrado
```

La cédula se utiliza únicamente para determinar si una persona tiene derecho a votar. La urna almacena el voto sin incluir la identidad.

---

## Idea general

El ciudadano se presenta físicamente en un punto de votación con su documento de identidad.

Un lector de documentos, cámara, dispositivo biométrico o ingreso manual controlado obtiene la identificación y consulta el registro electoral.

Para la prueba de concepto no disponemos de un escáner real. El lector se simula mediante una entrada por consola, porque el objetivo principal es demostrar el protocolo criptográfico.

El flujo es el siguiente:

1. El ciudadano presenta su documento.
2. La autoridad comprueba que la cédula esté registrada.
3. La autoridad verifica que la persona no haya votado anteriormente.
4. El ciudadano demuestra mediante Schnorr que conoce una clave privada asociada a su registro.
5. La clave privada nunca es revelada.
6. El sistema habilita una sesión de votación de un solo uso.
7. El ciudadano selecciona un candidato.
8. La selección se representa como un vector válido.
9. El voto se cifra y se almacena sin la cédula.
10. La autoridad marca que el ciudadano ya votó.
11. Al finalizar la elección, los votos se descifran y se contabilizan de forma agregada.

---

## Protocolo Schnorr

El prototipo utiliza el protocolo de identificación de Schnorr para demostrar conocimiento de una clave privada sin revelarla.

### Generación de claves

Se utilizan los parámetros públicos:

- `p`: número primo;
- `q`: orden del subgrupo;
- `g`: generador.

La clave privada del ciudadano es:

```text
x ∈ Zq
```

La clave pública correspondiente es:

```text
y = g^x mod p
```

La autoridad registra `y`, pero no necesita conocer `x`.

### Protocolo de autenticación

1. El ciudadano genera un número aleatorio `r`.
2. Calcula un compromiso:

```text
t = g^r mod p
```

3. La autoridad genera un desafío aleatorio `c`.
4. El ciudadano calcula:

```text
s = r + c·x mod q
```

5. La autoridad verifica:

```text
g^s mod p = t · y^c mod p
```

Si la igualdad se cumple, el ciudadano demuestra que conoce la clave privada correspondiente a la clave pública registrada.

La clave privada nunca se transmite.

---

## Representación del voto

Cada voto se representa mediante un vector *one-hot*.

Si existen `n` candidatos, el vector debe cumplir:

```text
vᵢ ∈ {0, 1}
Σvᵢ = 1
```

Por ejemplo, para dos candidatos:

```text
[1, 0] -> candidato 1
[0, 1] -> candidato 2
```

Los siguientes vectores serían inválidos:

```text
[0, 0] -> ningún candidato
[1, 1] -> más de un candidato
[2, 0] -> valor fuera del dominio permitido
```

---

## Cifrado de la papeleta

El prototipo cifra el vector utilizando **AES-256-GCM**.

Este modo proporciona:

- confidencialidad;
- integridad del ciphertext;
- autenticación del contenido;
- detección de modificaciones;
- un `nonce` diferente para cada voto.

La urna almacena únicamente:

```text
ciphertext
nonce
tag
```

Al cerrar la elección, las papeletas se descifran y sus vectores se suman para obtener los resultados.

---

## ZKP de validez del voto

El objetivo final es que la urna pueda comprobar la siguiente afirmación sin conocer el candidato:

> “La papeleta cifrada contiene exactamente un valor igual a `1` y todos los demás valores son `0`”.

La prueba debe garantizar que:

1. cada componente del vector pertenece al conjunto `{0, 1}`;
2. la suma de sus componentes es exactamente `1`;
3. la prueba corresponde a la papeleta almacenada;
4. no se revela la posición del valor `1`.

---

## Prevención del voto doble

El prototipo mantiene dos estructuras:

```text
registered
already_voted
```

`registered` contiene los ciudadanos autorizados y sus claves públicas.

`already_voted` contiene los identificadores de los ciudadanos que ya emitieron un voto.

La cédula no se almacena directamente. Se calcula:

```text
SHA-256(cédula)
```

Antes de habilitar la votación se comprueba que el hash:

- exista en el registro;
- no se encuentre en `already_voted`.

Después de registrar el voto, el hash se marca como utilizado.

---

## Estructura del repositorio

```text
zkp-voting/
├── main.py
├── schnorr.py
└── voting.py
```

### `main.py`

Controla el flujo de la demostración:

- registra ciudadanos;
- recibe la cédula;
- consulta la elegibilidad;
- ejecuta Schnorr;
- recibe la selección;
- cifra y registra el voto;
- marca al ciudadano como votante;
- cierra la elección.

### `schnorr.py`

Implementa:

- parámetros criptográficos;
- generación de claves;
- compromiso;
- desafío;
- respuesta;
- verificación de la prueba.

### `voting.py`

Contiene:

- modelos de ciudadanos y papeletas;
- autoridad electoral;
- hashing de identificadores;
- prevención del voto doble;
- creación del vector;
- cifrado AES-GCM;
- descifrado y conteo.

---

## Instalación

### Requisitos

- Python 3.10 o superior.
- `pip`.

### Crear un entorno virtual

```bash
python -m venv .venv
```

Linux o macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Instalar dependencias

```bash
pip install pycryptodome
```

### Ejecutar

```bash
python main.py
```

---

## Datos de demostración

El programa registra inicialmente estas cédulas:

```text
100000001
100000002
100000003
```

Si se ingresa una cédula registrada, el sistema ejecuta Schnorr y habilita la votación.

Si se intenta utilizar nuevamente la misma cédula, el voto es rechazado.

Al ingresar:

```text
0
```

la elección se cierra y se muestran los resultados agregados.

> La impresión del vector seleccionado solamente debe utilizarse durante el desarrollo. En la demostración final debería eliminarse para no mostrar explícitamente el voto.
