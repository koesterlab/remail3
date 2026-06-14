remail
======

ReMail - Email management with AI-powered features

For New Developers
==================

Getting Started
---------------

This project uses `Pixi <https://pixi.sh>`_ for dependency management and task execution.
Pixi provides a fast, cross-platform package manager that handles both conda and PyPI packages.

Prerequisites
~~~~~~~~~~~~~

Install Pixi::

    curl -fsSL https://pixi.sh/install.sh | bash

Setup
~~~~~

Clone and install dependencies::

    git clone https://github.com/koesterlab/remail2.git
    cd remail2
    pixi install

Available Commands
------------------

The project includes several pixi tasks defined in ``pixi.toml``:

* ``pixi run test`` – Run the test suite with pytest
* ``pixi run lint`` – Check code for linting errors with Ruff
* ``pixi run format-lint`` – Apply Ruff auto-fixes
* ``pixi run format-code`` – Run Ruff formatter only
* ``pixi run format`` – Run both formatting tasks
* ``pixi run format-check`` – Check formatting and linting without changes
* ``pixi run typecheck`` – Run mypy
* ``pixi run deadcode`` – Identify unused code paths
* ``pixi run security`` – Execute Bandit security scans

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   docs/api/modules

Development Workflow
--------------------

#. Make your changes
#. Format your code::

      pixi run format

#. Run tests::

      pixi run test

#. Create a pull request

CI/CD Workflows
---------------

Code Quality
~~~~~~~~~~~~

Runs on all pull requests to ``main``:

* Runs test suite
* Checks code linting
* Verifies formatting
* Runs mypy
* Executes Vulture
* Executes Bandit

Auto-assign Author
~~~~~~~~~~~~~~~~~~

Automatically assigns pull requests to their author.

Dependabot Auto-merge
~~~~~~~~~~~~~~~~~~~~~

Automatically approves and merges Dependabot pull requests for patch and minor updates.

Tech Stack
----------

* Python 3.12+
* Database: SQLite with SQLModel ORM
* Frontend: Streamlit / Flet
* AI/LLM: LlamaIndex, ChromaDB, Hugging Face embeddings
* Email: IMAP and Exchange protocol support
* Code Quality: Ruff, pytest

Utils
-----

* ``remail/util/request.py`` – ``RequestBuilder`` utility
* ``tests/utils/test_request.py`` – usage examples and tests



