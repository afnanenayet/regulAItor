# regulAItor

This is the code repo for the "regulAItor" hackathon project in the Berkeley LLM
MOOC.

# Setup

# Prerequisites

Install with the package manager of your choice:

* [uv](https://docs.astral.sh/uv/)
* [direnv](https://direnv.net/)
* [pyenv](https://github.com/pyenv/pyenv)
* [pre-commit](https://pre-commit.com)

## Actions

Install the listed packages using your package manager of choice. I would recommend
using [Homebrew](https://brew.sh/) where possible if on macOS (though not all packages are on there)
and WSL if you're on Windows. Linux users should already know what they're doing :).

Set up pre-commit hooks by running: `pre-commit install`. This will run basically quality
checks before any commit.

Set up the virtual environment by running `uv venv`.

Run `direnv allow` in your shell so that the virtual environment is loaded whenever
you navigate to the directory.

# Running FDA summarizer locally

You can run the streamlit dashboard for extracting FDA warning letter summaries locally.
Simply run:

```bash
./scripts/run_dashboard.bash
```

This script will run streamlit for you.

# Run full app locally

See the [Agent readme](/src/Framework/README.md).

You can also run it with docker compose. Make sure you have a `.env` file in the root
of the git repository with your OpenAI API credentials, then run `docker compose up`, and
the streamlit frontend will run.
