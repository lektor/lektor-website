# Lektor Website

This is the repository for the Lektor website at
[getlektor.com](https://www.getlektor.com/).

To run:

```
$ lektor server
```

If you also want to update the webpack files, you need `npm` installed
and then run it like this:

```
$ lektor server -f webpack
```

## Notes

Changes made here get deployed automatically by [this workflow](https://github.com/lektor/lektor-website/blob/master/.github/workflows/deploy.yml).

Building lektor-website requires the latest stable release of [Lektor](https://pypi.org/project/Lektor/).
