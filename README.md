# naive_tex_to_lean

A tool that takes a LaTeX file (.tex) as input and produces a text file (.txt) containing the document body, translated into syntax resembling the Lean Theorem Prover.

## Usage

The main script to run the full process is `process_tex_file.py`. Execute it from your terminal:

```bash
python process_tex_file.py <path_to_input.tex> <path_to_output.txt>
```

**Example:**

```bash
python process_tex_file.py path/to/my_paper.tex path/to/output/my_paper_lean_like.txt
```

## Installation

1.  Ensure you have Python 3 installed.
2.  Clone this repository (or download the files).
3.  Install the specific dependency:
    ```bash
    pip install pylatexenc==2.10
    ```
    **Note:** This project relies **strictly** on `pylatexenc==2.10`. It is not compatible with `pylatexenc` version 3.x or other versions due to significant API changes.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/justincasher/naive_tex_to_lean/blob/main/LICENSE) file for details.
