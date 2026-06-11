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
    assert "![](images/" not in cleaned
    assert "<details>" not in cleaned
    assert "```mermaid" not in cleaned
    assert "## Title" in cleaned
    assert "Bullet line" in cleaned
