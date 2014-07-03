function hljs_initGuessOnLoad() {
    addEventListener('DOMContentLoaded', hljs_initGuessHighlighting, false);
    addEventListener('load', hljs_initGuessHighlighting, false);
}

function hljs_initGuessHighlighting() {
    var elements = document.querySelectorAll('pre code'),
        elength = elements.length,
        clenght, i, j, classes, m, language, obj, code, index;

    if (hljs_initGuessHighlighting.called) {
        return;
    }
    hljs_initGuessHighlighting.called = true;

    for (i = 0; i < elength; i++) {
        code = elements[i]
        classes = code.className.split(' ');
        language = null;
        clength = classes.length
        for (j=0; j < clength; j++) {
            hasLang = new RegExp(/^language-([^\s]+)$/)
            m = hasLang.exec(classes[j]);
            if (m) {
                index = j;
                language = m[1];
                break;
            }
        }
        obj = hljs.highlightAuto(code.textContent)
        code.innerHTML = obj.value;
        if (language) {
            classes[index] = "hljs " + obj.language;
        } else {
            classes.push("hljs " + obj.language)
        }
        code.className = classes.join(" ");
        code.parentNode.className += " hljs";
    }
}

hljs_initGuessOnLoad();
