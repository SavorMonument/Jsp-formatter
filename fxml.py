#!/usr/bin/env python3

import sys
import os
import re

from collections import namedtuple, deque

TAG = namedtuple("TAG", ["text", "start", "end", "type"])

ERROR_BANNER = "<!-- ^^^ =====  ERROR  =====  ^^^ -->"

WHITESPACE = "  "
NON_WHITESPACE_RE = re.compile("[^\s]")
TAG_RE = re.compile("""<(?:"[^"]*"['"]*|'[^']*'['"]*|[^'">])+>""")
WORD_RE = re.compile("(?:\w+\W)")
HTML_COMMENT_RE = re.compile("<!--.*-->")

STATE_NORMAL = 0
STATE_STYLE = 1
STATE_SCRIPT = 2

def tag_iter(content):
    state = STATE_NORMAL
    idx = 0

    while idx < len(content):

        if state == STATE_NORMAL:
            match = TAG_RE.search(content, idx)
            if not match:
                return
            idx = match.end()
            if "script" in match.string:
                state = STATE_SCRIPT
            elif "style" in match.string:
                state = STATE_STYLE
        else:
            while state != STATE_NORMAL:
                match = TAG_RE.search(content, idx)
                if not match:
                    return
                idx = match.end()
                if state == STATE_SCRIPT and "script" in match.string:
                    state = STATE_NORMAL
                elif state == STATE_STYLE and "style" in match.string:
                    state = STATE_NORMAL

        
        tag_text = match.string[match.start():match.end()]
        type_match = WORD_RE.search(tag_text)
        ttype = type_match.string[type_match.start():type_match.end()-1]
        yield TAG(tag_text, match.start(), match.end(), ttype)

def is_comment(tag):
    return HTML_COMMENT_RE.search(tag.text) is not None

def is_taglib(tag):
    return tag.type == "taglib"

def is_jsp(tag):
    return tag.text.startswith("<%@")

def is_self_closed(tag):
    return tag.text[-2] == "/"

def is_closing_tag(tag):
    return tag.text[1] == "/"

def is_meta_info(tag):
    return tag.text[1] == "!"

def needs_indent(tag):
    needs_indent = True
    needs_indent = needs_indent and not is_comment(tag)
    needs_indent = needs_indent and not is_taglib(tag)
    needs_indent = needs_indent and not tag.type == "br"
    needs_indent = needs_indent and not tag.type == "b"
    needs_indent = needs_indent and not tag.type == "i"
    needs_indent = needs_indent and not is_self_closed(tag)
    needs_indent = needs_indent and not is_meta_info(tag)
    needs_indent = needs_indent and not is_jsp(tag)
    return needs_indent

def are_matching(open_tag, close_tag):
    # print(open_tag, close_tag)
    return open_tag.type == close_tag.type\
            and is_closing_tag(close_tag) and not is_closing_tag(open_tag)

def is_inline_tag(first_tag, second_tag, text):
    if os.linesep in text: return True

    is_inline_tag = False
    is_inline_tag = is_inline_tag or second_tag.type == "option"
    is_inline_tag = is_inline_tag or second_tag.type == "td"
    is_inline_tag = is_inline_tag or second_tag.type == "th"
    is_inline_tag = is_inline_tag or second_tag.type == "title"
    is_inline_tag = is_inline_tag or second_tag.type == "label"
    is_inline_tag = is_inline_tag or second_tag.type == "span"
    is_inline_tag = is_inline_tag or second_tag.type in ["h1", "h2", "h3", "h4", "h5", "h6"]

    return is_inline_tag

def assemble1(content):
    tag_stack = deque()

    tags = [tag for tag in tag_iter(content)]
    out_lines = []

    for idx, tag in enumerate(tags):

        # Text part
        if idx > 0:
            text = content[tags[idx-1].end: tag.start].strip()
            if len(text):
                if is_inline_tag(tags[idx-1], tag, ""):
                    out_lines[-1] += text
                else:
                    out_lines.append(WHITESPACE * len(tag_stack) + text)

        # Tag part
        if is_closing_tag(tag):
            if len(tag_stack) and not are_matching(tag_stack[-1], tag):
                out_lines.append("")
                out_lines.append(WHITESPACE * len(tag_stack) + ERROR_BANNER)
                out_lines.append("")

            open_tag = tag_stack.pop()
            text = content[open_tag.end: tag.start]
            if is_inline_tag(open_tag, tag, ""):
                out_lines[-1] += tag.text;
            else:
                out_lines.append(WHITESPACE * len(tag_stack) + tag.text)
        elif needs_indent(tag):
            out_lines.append(WHITESPACE * len(tag_stack) + tag.text)
            tag_stack.append(tag)
        else:
            out_lines.append(WHITESPACE * len(tag_stack) + tag.text)

    return os.linesep.join(out_lines)

if __name__ == "__main__":

    with open(sys.argv[1]) as f:
        content = f.read()

    content.replace(ERROR_BANNER, "")
    content = assemble1(content)

    print(content)
    sys.exit(0)
