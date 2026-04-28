import nh3

_ALLOWED_TAGS: frozenset[str] = frozenset({
    "p", "br", "strong", "em", "u", "s",
    "ul", "ol", "li",
    "h2", "h3", "h4",
    "blockquote",
    "a", "img",
    "table", "thead", "tbody", "tr", "td", "th",
    "figure", "figcaption",
    "hr",
})

_ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {"href", "rel", "target"},
    "img": {"src", "alt", "class", "style"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
    "*": {"class"},
}


def sanitize_html(value: str) -> str:
    """Очищає HTML від потенційно небезпечних тегів та атрибутів."""
    return nh3.clean(value, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS)
