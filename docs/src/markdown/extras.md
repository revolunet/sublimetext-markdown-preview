# Extras

## MathJax Support

To render Tex style math in Markdown, you can use the default MathJax configuration that is included with Markdown Preview or create and reference your own.

When using Python Markdown (the `markdown` parser), it is recommended to use something like the extension [`pymdownx.arithmatex`][arithmatex] as it ensures that math notation is preserved in the Markdown conversion process. GitHub (the `github` parser) does not have such an extension, so you might have to escape accordingly.

In this example, we will try to show a generalized approach that should work when using Python Markdown with `pymdownx.arithmatex` or GitHub (though preservation of math in GitHub may or may not be problematic).

Markdown Preview provides a generalized script in `Markdown Preview/js/math_config.js`. It searches for `#!tex $...$`, `#!tex $$...$$`, `#!tex \(...\)`, and `#!tex \[...\]`. You can change this to only target what you want by creating your own.

To load MathJax support, simply include the MathJax library along with the math config file provided by this extension. You are free to provide your own if you'd like to tweak the configuration:

```js
    "js": [
        "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js",
        "res://Markdown Preview/js/math_config.js"
    ]
```

If you are using `pymdownx.arithmatex` you can configure like so to take advantage of the generalized configuration.  You are also free to customize Arithmatex to target only what you want and output in the different forms. Check out Arithmatex documentation for more info.

```js
    "markdown_extensions": {
        "pymdownx.arithmatex": {
            "generic": true
        }
    }
```

## UML Support

If you are using the extension [SuperFences extension][superfences], it has an option to create special, custom fences. By default, it specifies `flow` and `sequence` languages to generate special code blocks that JavaScript can be applied to later to create UML diagrams: see [documentation][custom-fences] for more info. Assuming you are using SuperFences, you can include the following libraries to transform `sequence` and `flow` blocks using [js-sequence-diagrams][sequence] and [flowchart.js][flow] respectively.

```js
    "js": [
        // Required libraries to transform UML notation
        "https://cdnjs.cloudflare.com/ajax/libs/raphael/2.2.7/raphael.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.8.3/underscore-min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/js-sequence-diagrams/1.0.6/sequence-diagram-min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.6.5/flowchart.min.js",

        // This library applies the above libraries to the fenced code blocks `flow` and `sequence`.
        "res://Markdown Preview/js/uml.js"
    ]
```

--8<-- "refs.md"
