import ace from 'ace-builds/src-noconflict/ace';
import 'ace-builds/src-noconflict/mode-text';

const oop = ace.acequire('ace/lib/oop');
const TextMode = ace.acequire('ace/mode/text').Mode;
const TextHighlightRules = ace.acequire('ace/mode/text_highlight_rules').TextHighlightRules;

const LALGHighlightRules = function () {
  this.$rules = {
    start: [
      { token: 'comment.line', regex: '//.*?(?=\\n|$)' },
      { token: 'comment.block', regex: '\\{.*?\\}' },

      { token: 'keyword.control', regex: '\\b(program|procedure|begin|end|if|then|var|else|while|do|not|and|or)\\b' },
      { token: 'constant.language', regex: '\\b(true|false)\\b' },
      { token: 'keyword.operator', regex: ':=|=|<>|<=|>=|<|>' },
      { token: 'keyword.operator.arithmetic', regex: '\\+|\\-|\\*|\\bdiv\\b' },

      { token: 'storage.type', regex: '\\b(int|boolean)\\b' },
      { token: 'constant.numeric', regex: '\\b[0-9]+\\.[0-9]+\\b' }, // real
      { token: 'constant.numeric', regex: '\\b[0-9]+\\b' }, // integer

      { token: 'identifier', regex: '\\b[a-zA-Z_][a-zA-Z0-9_]*\\b' },

      { token: 'paren.lparen', regex: '[\\(]' },
      { token: 'paren.rparen', regex: '[\\)]' },
      { token: 'punctuation.comma', regex: ',' },
      { token: 'punctuation.semicolon', regex: ';' },
      { token: 'punctuation.colon', regex: ':' },
      { token: 'punctuation.dot', regex: '\\.' },
    ],
  };

  this.normalizeRules();
};

oop.inherits(LALGHighlightRules, TextHighlightRules);

export const LALGMode = function () {
  this.HighlightRules = LALGHighlightRules;
};
oop.inherits(LALGMode, TextMode);
