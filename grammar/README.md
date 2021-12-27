## Grammar

### A pretty cool module just for fixing danish grammar. 

Needs the proper version of spacy and the large danish model.

#### Features

- [x] Corrects `at` vs `og`, using BERT unmasker.
- [x] Corrects `af` vs `ad`, using BERT unmasker.
- [x] Checks proper tense (nutids-r).
- [ ] Checks proper congruency (amounts and consistency).
- [x] Corrects `en` vs `et`.
- [x] Corrects `ligger` vs `lægger.`
- [x] Capitalizes names.

#### Fixes

- [ ] Simple listing commas should only put a comma in front of a PROPN, if it is in the list of names.
