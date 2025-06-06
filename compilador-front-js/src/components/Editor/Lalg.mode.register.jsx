// src/modes/register-lalg-mode.js
import ace from 'ace-builds/src-noconflict/ace';
import { LALGMode } from './Lalg.mode';

ace.define('ace/mode/lalg', [], function(require, exports) {
  exports.Mode = LALGMode;
});
