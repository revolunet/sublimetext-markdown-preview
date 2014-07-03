function hljs_initNoGuessOnLoad() {
    addEventListener('DOMContentLoaded', hljs_initNoGuessHighlighting, false);
    addEventListener('load', hljs_initNoGuessHighlighting, false);
}

function hljs_initNoGuessHighlighting() {
    var elements = document.querySelectorAll('pre code'),
        elength = elements.length,
        clenght, i, j, classes, m, language, obj, code, index;

    if (hljs_initNoGuessHighlighting.called) {
        return;
    }
    hljs_initNoGuessHighlighting.called = true;

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
        if (language) {
            obj = hljs.highlight(language, code.textContent, true)
            code.innerHTML = obj.value;
            classes[index] = "hljs " + obj.language;
            code.className = classes.join(" ");
            code.parentNode.className += " hljs";
        } else {
            code.className += " hljs";
            code.parentNode.className += " hljs";
        }
    }
}

hljs_initNoGuessOnLoad();
