# Lektor Website

This is the repository for the Lektor website at [getlektor.com].

## Development / Editing the Website

To work on this project locally:

First, ensure that you have both [uv] and [node] installed.

Then:
```sh
$ git clone https://github.com/lektor/lektor-website.git
$ cd lektor-website
$ uv run lektor -f webpack server
```

You should now be able to access the Lektor admin UI by pointing your
web browser at http://localhost:5000/.

## Tests

Running

```sh
$ uv run noxfile.py
```

will build the project.

If you have [htmltest] installed (somewhere in your `$PATH`), then you may run

```sh
$ uv run noxfile -t tests
```

to build the project, then check internal links for validity.

## Notes

Changes made here get deployed automatically by [this workflow][deploy.yml].

[getlektor.com]: https://www.getlektor.com/
[uv]: https://docs.astral.sh/uv/
[node]: https://nodejs.org/
[htmltest]: https://github.com/wjdp/htmltest
[deploy.yml]: https://github.com/lektor/lektor-website/blob/master/.github/workflows/deploy.yml
