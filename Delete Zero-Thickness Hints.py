#MenuTitle: Delete Zero-Thickness Hints
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
Removes all zero-thickness hints from all glyphs in the font.

'''

from GlyphsApp import *

doc = Glyphs.currentDocument
font = doc.font

deletions_count = 0
for glyph in font.glyphs:
	for layer in glyph.layers:
		for indx in range( len( layer.hints ) - 1, -1, -1 ):
			hint = layer.hints[indx]
			if hint.targetNode:
				if hint.horizontal:
					if hint.originNode.y == hint.targetNode.y:
						del( layer.hints[indx] )
						deletions_count += 1
						print 'deleted zero-width hint from', glyph.name
				else:
					if hint.originNode.x == hint.targetNode.x:
						del( layer.hints[indx] )
						deletions_count += 1
						print 'deleted zero-width hint from', glyph.name

Message( 'Delete Zero-Thickness Hints', 'Deleted %i hints.' % deletions_count )
