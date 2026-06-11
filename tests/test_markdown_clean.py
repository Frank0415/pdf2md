from pdf2md.markdown_clean import strip_sup_markup, to_clear_markdown


def test_unwraps_paired_sup_tags():
    raw = "• <sup>Node</sup> <sup>manager</sup> <sup>failure</sup>"
    assert strip_sup_markup(raw) == "• Node manager failure"


def test_removes_orphan_sup_fragments():
    raw = "hello </sup> world <sup> there"
    assert strip_sup_markup(raw) == "hello  world  there"


def test_preserves_non_sup_content():
    raw = "## Title\n\nNormal **bold** text."
    assert strip_sup_markup(raw) == raw


def test_strips_mineru_artifacts():
    raw = """![](images/foo.jpg)

<details><summary>x</summary>
hidden
</details>

## Title

```mermaid
graph TD
  A-->B
```

Bullet line
"""
    cleaned = to_clear_markdown(raw)
    assert "![](images/foo.jpg)" in cleaned
    assert "<details>" not in cleaned
    assert "hidden" not in cleaned
    assert "```mermaid" not in cleaned
    assert "## Title" in cleaned
    assert "Bullet line" in cleaned


def test_strips_mineru_image_descriptions():
    raw = """![diagram](images/foo.jpg)

<details>
<summary>natural_image</summary>

Cartoon illustration of a yellow elephant with a cheerful expression (no text or symbols)
</details>

## Title
"""
    cleaned = to_clear_markdown(raw)
    assert "![](images/foo.jpg)" in cleaned
    assert "## Title" in cleaned
    assert "illustration" not in cleaned
    assert "natural_image" not in cleaned


def test_strips_image_alt_text():
    raw = "![A Hadoop flowchart](images/foo.jpg)\n"
    assert to_clear_markdown(raw) == "![](images/foo.jpg)\n"
