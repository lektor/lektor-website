# Lektor Website

This is the repository for the Lektor website at
[getlektor.com](https://www.getlektor.com/).

We currently use PDM to manage dependencies and scripts.

To run:

1. First install [PDM](https://pdm.fming.dev/latest/#installation), and [node.js/npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

2. Install python dependencies

```sh
$ pdm install
```

3. Run Lektor dev server

```sh
$ pdm run server
```

or just build the site to `./_htdocs/`

```sh
$ pdm run build
```



## Notes

Changes made here get deployed automatically by [this workflow](https://github.com/lektor/lektor-website/blob/master/.github/workflows/deploy.yml).

Building lektor-website requires the latest stable release of [Lektor](https://pypi.org/project/Lektor/).
