import nox  # type: ignore
from pathlib import Path
import shutil

nox.options.sessions = ["tests", "lint", "docs"]


@nox.session(python=["3.5", "3.6", "3.7", "3.8"])
def tests(session):
    session.install(".")
    session.run("python", "-m", "unittest", "discover")


@nox.session(python="3.7")
def lint(session):
    session.install(*["black", "flake8", "mypy", "check-manifest"])
    files = ["pygdbmi", "tests"] + [str(p) for p in Path(".").glob("*.py")]
    session.run("black", "--check", *files)
    session.run("flake8", *files)
    session.run("mypy", *files)  #
    session.run("check-manifest")
    session.run("python", "setup.py", "check", "--metadata", "--strict")


@nox.session(python="3.7")
def docs(session):
    session.install(".", "pdoc3")
    session.run(
        "pdoc", "--html", "--force", "--output-dir", "/tmp/pygdbmi_docs", "pygdbmi"
    )
    shutil.rmtree("docs", ignore_errors=True)
    shutil.move("/tmp/pygdbmi_docs/pygdbmi", "docs")


@nox.session(python="3.7")
def publish_docs(session):
    session.run("git", "checkout", "gh-pages", external=True)
    session.run("git", "rebase", "master", external=True)
    docs(session)
    session.run("git", "add", "docs", external=True)
    session.run("git", "commit", "-m", "updating docs", external=True)
    session.run("git", "push", "origin", "gh-pages", external=True)


@nox.session(python="3.7")
def build(session):
    session.install("setuptools", "wheel", "twine")
    shutil.rmtree("dist", ignore_errors=True)
    session.run("python", "setup.py", "--quiet", "sdist", "bdist_wheel")
    session.run("twine", "check", "dist/*")


@nox.session(python="3.7")
def publish(session):
    build(session)
    print("REMINDER: Has the changelog been updated?")
    session.run("python", "-m", "twine", "upload", "dist/*")
