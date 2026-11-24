# Smart Calculator

A safe calculator with a Streamlit web interface. Expressions are parsed into a syntax tree and only whitelisted numbers, operators and functions run, so user input can never execute code.

## Files

| File | Purpose |
| --- | --- |
| `calculator.py` | The calculator engine, plus a command-line version (`python calculator.py`) |
| `app.py` | The Streamlit web app |
| `requirements.txt` | Packages Streamlit Cloud installs |
| `.streamlit/config.toml` | Theme and server settings |
| `test_calculator.py`, `test_app.py` | Tests (`pip install pytest`, then `pytest`) |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud (free)

1. Create a new public GitHub repository, for example `smart-calculator`.
2. Upload every file in this folder, keeping `.streamlit/config.toml` inside a `.streamlit` folder.
3. Go to https://share.streamlit.io and sign in with GitHub.
4. Click **Create app**, then **Deploy a public app from GitHub**.
5. Choose your repository, branch `main`, and main file path `app.py`.
6. Optional: under **Advanced settings**, pick Python 3.12, and set a custom URL such as `kat-smart-calculator`.
7. Click **Deploy**. The first build takes 1 to 3 minutes.

Every push to `main` redeploys the app automatically.

## What users can type

`+ - * /` (also `x`, `×`, `÷`), `^` or `**` for powers, `//`, `%` for remainder, `sqrt()`, `abs()`, `round()`, `log()`, `ln()`, `sin()`, `cos()`, `tan()` (degrees), `factorial()`, `pi`, `e`, and `ans` for the previous answer. Commas in numbers like `1,000` are accepted.
