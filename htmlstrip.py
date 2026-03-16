#!/usr/bin/env python3
"""htmlstrip - Strip HTML tags and extract text content."""
import html.parser, argparse, sys, re, urllib.request, json

class TextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.images = []
        self.skip = False
        self._tag_stack = []
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ('script', 'style', 'noscript'):
            self.skip = True
        elif tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])
        elif tag == 'img' and 'src' in attrs_dict:
            self.images.append(attrs_dict.get('alt', attrs_dict['src']))
        elif tag in ('br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'):
            self.text.append('\n')
        self._tag_stack.append(tag)
    
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.skip = False
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
    
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

def main():
    p = argparse.ArgumentParser(description='Strip HTML tags')
    p.add_argument('input', nargs='?', help='HTML file or URL')
    p.add_argument('--links', action='store_true', help='Extract links')
    p.add_argument('--images', action='store_true', help='Extract images')
    p.add_argument('-o', '--output')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    if args.input and args.input.startswith('http'):
        with urllib.request.urlopen(args.input) as r:
            html_text = r.read().decode(errors='replace')
    elif args.input:
        with open(args.input) as f: html_text = f.read()
    else:
        html_text = sys.stdin.read()

    ext = TextExtractor()
    ext.feed(html_text)
    text = ''.join(ext.text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    if args.json:
        result = {'text': text, 'links': ext.links, 'images': ext.images}
        output = json.dumps(result, indent=2)
    elif args.links:
        output = '\n'.join(ext.links)
    elif args.images:
        output = '\n'.join(ext.images)
    else:
        output = text

    if args.output:
        with open(args.output, 'w') as f: f.write(output)
    else:
        print(output)

if __name__ == '__main__':
    main()
