from typing import NamedTuple


class Search(NamedTuple):
    description: str
    regexes: dict[str, str]
    files: dict[str, str] = {}


CODE_FILE = r"\.(py|ts|tsx|js|jsx|mjs|cjs|vue|css|scss|html|sh|java|kt|go|rs|sql)$"
TEST_FILE = r"(^|/)(tests?|__tests__|e2e|testdata)/|\.(spec|test)\."
NON_BLANK = r"[^[:space:]]"
_COMMENT_LINE = r"^[[:space:]]*(//|/\*|\*+( |/|$)|<!--|#( |!|$)|-- )"
_HASH_COMMENT_FILE = r"\.(py|sh)$"
_SLASH_COMMENT_FILE = r"\.(ts|tsx|js|jsx|mjs|cjs|vue|scss|java|kt|go|rs)$"

SEARCHES = {
    "vue-class": Search("Vue class components vs. script setup",
                        {"Old simple": r"extends Vue", "Old mixin": r"extends mixins", "New": r"<script .*setup"}),
    "vue-setup": Search("Vue options API vs. script setup", {"Old": r"export default {", "New": r"<script .*setup"}),
    "link": Search("link_created vs. linkCreated", {"link": r"link_created", "link2": r"linkCreated"}),
    "todo": Search("TODOs", {"Todo": r"TODO"}),
    "sticky": Search("Sticky vs. card", {"Sticky": r"sticky", "Card": r"card"}),
    "types": Search("Loose types and disabled lint rules",
                    {"any": r"(: |<)any(>|[^a-zA-Z]|$)", "object": r"(: |<)object(>|[^a-zA-Z]|$)", "record": r"Record<",
                     "eslint disable ts": r"/[/*] eslint-disable", "eslint disable vue": r"<!-- eslint-disable"}),
    "loc": Search("Non-blank lines of code", {"Total": NON_BLANK, "Prod": NON_BLANK, "Test": NON_BLANK},
                  {"Total": CODE_FILE, "Prod": rf"^(?=.*({CODE_FILE}))(?!.*({TEST_FILE}))",
                   "Test": rf"^(?=.*({CODE_FILE}))(?=.*({TEST_FILE}))"}),
    "comments": Search("Comments",
                       {"Full line": _COMMENT_LINE, "End of line #": r"[^[:space:]].*[[:space:]]#( |$)",
                        "End of line //": r"[^[:space:]].*[[:space:]]//( |$)"},
                       {"Full line": CODE_FILE, "End of line #": _HASH_COMMENT_FILE,
                        "End of line //": _SLASH_COMMENT_FILE}),
}
