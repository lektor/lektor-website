# Lektor Website

This is the repository for the Lektor website at [getlektor.com].

We currently use [PDM] to manage dependencies and scripts.

To run:

First [install PDM], and [node.js/npm][install nodejs].

Next, install python dependencies

```sh
$ pdm install
```

Run the Lektor dev server

```sh
$ pdm run server
```

or just build the site to `./_htdocs/`

```sh
$ pdm run build
```

## Notes

Changes made here get deployed automatically by [this workflow][deploy.yml].

Building lektor-website requires the latest stable release of [Lektor].

[getlektor.com]: https://www.getlektor.com/
[PDM]: https://pdm-project.org/
[install PDM]: https://pdm-project.org/en/latest/#installation
[install nodejs]: https://nodejs.org/en/download/
[Lektor]: https://pypi.org/project/Lektor/
[deploy.yml]: https://github.com/lektor/lektor-website/blob/master/.github/workflows/deploy.yml
