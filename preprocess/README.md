## Preprocessing

### `datasplit.sh`

This script handles splitting of training, evaluation and test files.

Takes:

- `formatted.txt`

This file can be made using `gen.py`.

- `gen.py`

Generates a properly processed POS-token masked dataset.
Must be run as `__main__` with arguments being input and output, respectively.