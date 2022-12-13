# Compressor

Compress a one or many images at once.

## Installation

```bash
git clone https://github.com/marcusfrdk/compressor
cd compressor
pip install -r requirements.txt
```

## Usage

### Single file

```bash
python main.py path/to/image
```

### Current directory

```bash
python main.py
```

### Flags

| Flag          | Description                        | Type |
| ------------- | ---------------------------------- | ---- |
| path          | path to file or directory          | str  |
| -q, --quality | quality to compress with           | int  |
| -r, --replace | replace existing file              | bool |
| -m, --method  | method to compress with            | int  |
| -rm, --remove | delete all files containing '-min' | bool |
| -d, --dry     | runs the script without commiting  | bool |

### Aliasing

Add an alias to the `compressor/main.py` script to use the script anywhere.
