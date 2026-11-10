# Contributing / Cómo contribuir

> **Pull requests are not accepted yet / Aún no se aceptan pull requests.**
> **EN** — The maintainer may offer a commercial licence or premium content in the future. Code or content contributed under the plain open licences could not be relicensed, so **until a Contributor License Agreement (CLA) is in place, please open an issue or discussion instead of a pull request.** Ideas, bug reports and exercise suggestions are very welcome (describe them in your own words; the maintainer writes the final content).
> **ES** — El mantenedor podría ofrecer en el futuro una licencia comercial o contenido premium. El código o contenido aportado solo bajo las licencias abiertas no podría relicenciarse, así que **mientras no exista un Acuerdo de Licencia de Contribuyente (CLA), abre un issue o una discusión en lugar de un pull request.** Ideas, reportes de errores y sugerencias de ejercicios son bienvenidos (descríbelos con tus palabras; el mantenedor escribe el contenido final).
>
> The guidelines below apply once contributions open / Las pautas siguientes aplican cuando se abran las contribuciones.

## EN
Thanks for helping other job seekers practice! Please:
1. **Write your own exercises.** Do not copy statements, examples, test names or data from interview platforms, books, courses, or from interviews covered by an NDA. Algorithmic *ideas* are free; *wording and datasets* are protected. Read [docs/CONTENT-GUIDELINES.md](docs/CONTENT-GUIDELINES.md).
2. **Use a sector, never a company** (Amazon → e-commerce, American Airlines → airline).
3. Start from `python3 tools/new_problem.py my-id "Title"`. Provide EN **and** ES statements, and EN **and** ES feedback.
4. `python3 tools/validate.py` and `python3 -m unittest discover -s tests -t .` must pass with no warnings on built-in content.
5. Sign the CLA (to be published) and sign off your commits (`git commit -s`, [Developer Certificate of Origin](https://developercertificate.org/)). The CLA lets the project keep relicensing options; the DCO alone certifies origin but does **not** grant them.
6. Add yourself to `AUTHORS.md`.

## ES
¡Gracias por ayudar a otras personas a practicar! Por favor:
1. **Escribe tus propios ejercicios.** No copies enunciados, ejemplos, nombres de pruebas ni datos de plataformas de entrevistas, libros, cursos, ni de entrevistas cubiertas por un NDA. Las *ideas* algorítmicas son libres; la *redacción y los datos* están protegidos. Lee [docs/CONTENT-GUIDELINES.md](docs/CONTENT-GUIDELINES.md).
2. **Usa un giro, nunca una empresa** (Amazon → comercio electrónico, American Airlines → aerolínea).
3. Parte de `python3 tools/new_problem.py mi-id "Título"`. Entrega enunciados en EN **y** ES, y retroalimentación en EN **y** ES.
4. `python3 tools/validate.py` y `python3 -m unittest discover -s tests -t .` deben pasar sin avisos en el contenido incluido.
5. Firma el CLA (por publicar) y firma tus commits (`git commit -s`, [Certificado de Origen del Desarrollador](https://developercertificate.org/)). El CLA permite al proyecto conservar opciones de relicenciamiento; el DCO por sí solo certifica el origen pero **no** las otorga.
6. Agrégate a `AUTHORS.md`.
