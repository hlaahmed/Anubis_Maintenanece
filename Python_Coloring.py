from glob import glob
import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

extension_ = 'py'

def setExtension(extension):
    global extension_
    extension_=extension
    

def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages

STYLES2 = {
    'keyword': format([200, 120, 50], 'bold'),
    'operator': format([150, 150, 150]),
    'brace': format('darkGray'),
    'defclass': format([220, 220, 255], 'bold'),
    'string': format([20, 110, 100]),
    'string2': format([30, 120, 110]),
    'comment': format([128, 128, 128]),
    'this': format([150, 85, 140], 'italic'),
    'numbers': format([100, 150, 190]),
}
STYLES = {
       'keyword': format('blue'),
      'operator': format('red'),
       'brace': format('darkGray'),
       'defclass': format('black', 'bold'),
       'string': format('magenta'),
       'string2': format('darkMagenta'),
       'comment': format('darkGreen', 'italic'),
       'self': format('black', 'italic'),
       'numbers': format('brown'),
   }

class Highlighter(QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    pkeywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]
    # Python operators
    poperators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]
    # Python braces
    pbraces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    # C# keywords

    ckeywords = [
        'class', 'abstract','base','bool','break','byte','case','catch','char','const',
        'continue','decimal','do','double','else','enum','event','explicit',
        'extern','false','finally','fixed','float','for','foreach','goto','if','implicit','in','int',
        'interface','internal','lock','long','namespace','null','object','operator','out',
        'override','params','private','protected','public','readonly','ref','return','sbyte','sealed',
        'short','static','string','struct','switch','throw','true','try', 
        'uint','ulong','unsafe','ushort','using','virtual','void','volatile','while',
        
    ]

    # C# operators
    coperators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=', 
        '\&=', '\|=','\^=', '<<=', '>>=', '??=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
        # Primary
        '\++', '--','new', 'typeof','checked','unchecked','default', 'nameof', 'delegate','sizeof','stackalloc', 'is',
    ]
    # poperators = [
    #     '=',
    #     # Comparison
    #     '==', '!=', '<', '<=', '>', '>=',
    #     # Arithmetic
    #     '\+', '-', '\*', '/', '//', '\%', '\*\*',
    #     # In-place
    #     '\+=', '-=', '\*=', '/=', '\%=',
    #     # Bitwise
    #     '\^', '\|', '\&', '\~', '>>', '<<',
    # ]

    # C# braces
    cbraces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        prules = []

        # Keyword, operator, and brace rules
        prules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in Highlighter.pkeywords]
        prules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in Highlighter.poperators]
        prules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in Highlighter.pbraces]

        # All other rules
        prules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.prules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in prules]
        

        crules = []

        # Keyword, operator, and brace rules
        crules += [(r'\b%s\b' % w, 0, STYLES2['keyword'])
                  for w in Highlighter.ckeywords]
        crules += [(r'%s' % o, 0, STYLES2['operator'])
                  for o in Highlighter.coperators]
        crules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in Highlighter.cbraces]

        # All other rules
        crules += [
            # 'self'
            (r'\bthis\b', 0, STYLES2['this']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES2['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES2['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES2['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES2['defclass']),

            # From '//' until a newline
            (r'//[^\n]*', 0, STYLES2['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES2['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES2['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES2['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.crules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in crules]

        

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # extension = 'py'
        # Do other syntax formatting
        if(extension_=='py'):
            for expression, nth, format in self.prules:
                index = expression.indexIn(text, 0)

                while index >= 0:
                # We actually want the index of the nth match
                    index = expression.pos(nth)
                    length = len(expression.cap(nth))
                    self.setFormat(index, length, format)
                    index = expression.indexIn(text, index + length)
        else:
            for expression, nth, format in self.crules:
                index = expression.indexIn(text, 0)

                while index >= 0:
                # We actually want the index of the nth match
                    index = expression.pos(nth)
                    length = len(expression.cap(nth))
                    self.setFormat(index, length, format)
                    index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

# class CsHighlighter(QSyntaxHighlighter):
#     """Syntax highlighter for the C# language.
#     """
#     # C# keywords

#     keywords = [
#         'abstract','base','bool','break','byte','case','catch','char','const',
#         'continue','decimal','do','double','else','enum','event','explicit',
#         'extern','false','finally','fixed','float','for','foreach','goto','if','implicit','in','int',
#         'interface','internal','lock','long','namespace','null','object','operator','out',
#         'override','params','private','protected','public','readonly','ref','return','sbyte','sealed',
#         'short','static','string','struct','switch','throw','true','try',
#         'uint','ulong','unsafe','ushort','using','virtual','void','volatile','while',
#     ]

#     # C# operators
#     operators = [
#         '=',
#         # Comparison
#         '==', '!=', '<', '<=', '>', '>=',
#         # Arithmetic
#         '+', '-', '*', '/', '/', '%', '\*\*',
#         # In-place
#         '+=', '-=', '*=', '/=', '%=', '&=', '|=','^=', '<<=', '>>=', '??=', '=>'
#         # Bitwise
#         '^', '|', '&', '~', '>>', '<<',
#         #conditional
#         '&&','||','??',
#         # Primary
#         '++', '--','new', 'typeof','checked','unchecked','default', 'nameof', 'delegate','sizeof','stackalloc', '->', 'is','as', 'await'
#     ]

#     # C# braces
#     braces = [
#         '\{', '\}', '\(', '\)', '\[', '\]',
#     ]

#     def __init__(self, document):
#         QSyntaxHighlighter.__init__(self, document)

#         # Multi-line strings (expression, flag, style)
#         # FIXME: The triple-quotes in these two lines will mess up the
#         # syntax highlighting from this point onward
#         self.tri_single = (QRegExp("'''"), 1, STYLES2['string2'])
#         self.tri_double = (QRegExp('"""'), 2, STYLES2['string2'])

#         rules = []

#         # Keyword, operator, and brace rules
#         rules += [(r'\b%s\b' % w, 0, STYLES2['keyword'])
#                   for w in CsHighlighter.keywords]
#         rules += [(r'%s' % o, 0, STYLES2['operator'])
#                   for o in CsHighlighter.operators]
#         rules += [(r'%s' % b, 0, STYLES['brace'])
#                   for b in CsHighlighter.braces]

#         # All other rules
#         rules += [
#             # 'this'
#             (r'\bthis\b', 0, STYLES2['this']),

#             # Double-quoted string, possibly containing escape sequences
#             (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES2['string']),
#             # Single-quoted string, possibly containing escape sequences
#             (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES2['string']),

#             # 'def' followed by an identifier
#             (r'\bdef\b\s*(\w+)', 1, STYLES2['defclass']),
#             # 'class' followed by an identifier
#             (r'\bclass\b\s*(\w+)', 1, STYLES2['defclass']),

#             # From '//' until a newline
#             (r'///[^\n]*', 0, STYLES2['comment']),

#             # Numeric literals
#             (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES2['numbers']),
#             (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES2['numbers']),
#             (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES2['numbers']),
#         ]

#         # Build a QRegExp for each pattern
#         self.rules = [(QRegExp(pat), index, fmt)
#                       for (pat, index, fmt) in rules]

#     def highlightBlock(self, text):
#         """Apply syntax highlighting to the given block of text.
#         """
#         # Do other syntax formatting
#         for expression, nth, format in self.rules:
#             index = expression.indexIn(text, 0)

#             while index >= 0:
#                 # We actually want the index of the nth match
#                 index = expression.pos(nth)
#                 length = len(expression.cap(nth))
#                 self.setFormat(index, length, format)
#                 index = expression.indexIn(text, index + length)

#         self.setCurrentBlockState(0)

#         # Do multi-line strings
#         in_multiline = self.match_multiline(text, *self.tri_single)
#         if not in_multiline:
#             in_multiline = self.match_multiline(text, *self.tri_double)

#     def match_multiline(self, text, delimiter, in_state, style):
#         """Do highlighting of multi-line strings. ``delimiter`` should be a
#         ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
#         ``in_state`` should be a unique integer to represent the corresponding
#         state changes when inside those strings. Returns True if we're still
#         inside a multi-line string when this function is finished.
#         """
#         # If inside triple-single quotes, start at 0
#         if self.previousBlockState() == in_state:
#             start = 0
#             add = 0
#         # Otherwise, look for the delimiter on this line
#         else:
#             start = delimiter.indexIn(text)
#             # Move past this match
#             add = delimiter.matchedLength()

#         # As long as there's a delimiter match on this line...
#         while start >= 0:
#             # Look for the ending delimiter
#             end = delimiter.indexIn(text, start + add)
#             # Ending delimiter on this line?
#             if end >= add:
#                 length = end - start + add + delimiter.matchedLength()
#                 self.setCurrentBlockState(0)
#             # No; multi-line string
#             else:
#                 self.setCurrentBlockState(in_state)
#                 length = len(text) - start + add
#             # Apply formatting
#             self.setFormat(start, length, style)
#             # Look for the next match
#             start = delimiter.indexIn(text, start + length)

#         # Return True if still inside a multi-line string, False otherwise
#         if self.currentBlockState() == in_state:
#             return True
#         else:
#             return False