#MenuTitle: Mask to Master
# encoding: utf-8

# by Tim Ahrens
# http://justanotherfoundry.com
# https://github.com/justanotherfoundry/glyphsapp-scripts

__doc__='''
The selected nodes will adopt the position of the corresponding nodes in the background.
In combination with Insert Glyph to Background, you can easily
transfer parts of the outlines between glyphs.
'''

import sys
from AppKit import NSBeep

def counterparts( selection, background ):
	if background.components:
		# we cannot use background.copyDecomposedLayer() here
		# as this would also decompose caps and corners.
		# so, we need to manually create a decomposed copy:
		foregroundLayer = background.foreground()
		glyph = foregroundLayer.parent
		glyph_copy = glyph.copy()
		glyph_copy.parent = glyph.parent
		background = glyph_copy.layers[foregroundLayer.layerId].background
		background.decomposeComponents()
	best_point_range = []
	best_deviation = sys.maxsize
	# search in each path
	for bg_path in background.paths:
		bg_nodes = bg_path.nodes
		# try each starting point
		for start in range( len( bg_nodes ) ):
			indx = start
			deviation = 0
			point_range = []
			# calculate deviation
			for node in selection:
				bg_node = bg_nodes[indx]
				if ( node.type == OFFCURVE ) != ( bg_node.type == OFFCURVE ):
					break
				deviation += abs( node.x - bg_node.x )
				deviation += abs( node.y - bg_node.y )
				if deviation > best_deviation:
					break
				point_range.append( bg_node )
				# increase index looping around
				indx = ( indx + 1 ) % len( bg_nodes )
			else:
				best_deviation = deviation
				best_point_range = point_range
	return zip( selection, best_point_range )

def subpaths( selection ):
	selection.append( GSNode() )
	# build subpaths
	subpaths = []
	tail = []
	nextNode = None
	current_subpath = []
	current_subpath_is_tail = False
	for node in selection:
		if node == nextNode:
			current_subpath.append( node )
		else:
			if current_subpath_is_tail:
				if current_subpath[0] == nextNode:
					subpaths.append( current_subpath )
				else:
					tail = current_subpath
			else:
				if tail and tail[0] == nextNode:
					current_subpath.extend( tail )
					tail = []
				if current_subpath:
					subpaths.append( current_subpath )
			# start new subpath
			current_subpath = [ node ]
			# starting a new tail?
			if node.prevNode in selection:
				current_subpath_is_tail = True
				tail = [ node ]
			else:
				current_subpath_is_tail = False
		nextNode = node.nextNode
	return subpaths

layer = Glyphs.font.selectedLayers[0]
glyph = layer.parent
selection = [ node for path in layer.paths for node in path.nodes if node in layer.selection ]

any_changes = False
if selection:
	subpaths = subpaths( selection )
	for subpath in subpaths:
		for node, bg_node in counterparts( subpath, layer.background ):
			if not any_changes:
				if node.position == bg_node.position:
					continue
				else:
					any_changes = True
					glyph.beginUndo()
					layer.beginChanges()
			node.position = bg_node.position
else:
	decomposed_bg = layer.background.copyDecomposedLayer()
	if len( layer.paths ) != len( decomposed_bg.paths ):
		any_changes = True
	else:
		for path, bg_path in zip(layer.paths, decomposed_bg.paths):
			if len( path.nodes ) != len( bg_path.nodes ):
				any_changes = True
				break
			else:
				for node, bg_node in zip(path.nodes, bg_path.nodes):
					if node.position != bg_node.position:
						any_changes = True
						break
	if any_changes:
		glyph.beginUndo()
		layer.beginChanges()
		try:
			while layer.shapes:
				del(layer.shapes[0])
		except:
			while layer.paths:
				del(layer.paths[0])
		for path in decomposed_bg.paths:
			layer.paths.append( path.copy() )
if any_changes:
	layer.syncMetrics()
	layer.endChanges()
	glyph.endUndo()
else:
	NSBeep()
