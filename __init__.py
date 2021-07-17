bl_info = {
	"name": "Favorite Image List",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "Image Editor/UV Editor > Properties (N) > Favs Tab",
	"description": "Adds a favorite images list for fast image switching.",
	"warning": "",
	"wiki_url": "",
	"category": "Image"
}

import bpy
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty, BoolProperty, FloatProperty, StringProperty, PointerProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel, AddonPreferences

## Helper Functions



## Structs

class FaveImageListPropertyGroup(PropertyGroup):
	image_name : StringProperty()


## Operators

class FIL_OT_add_to_faves(Operator):
	"""Adds current image to favorites."""
	bl_idname = "image.fil_ot_add_to_faves"
	bl_label = "Add to Fave Images"
	"""
		REGISTER
			Display in info window and support redo toolbar panel
		UNDO
			Push an undo event, needed for operator redo
		BLOCKING
			Block anthing else from moving the cursor
		MACRO
			?
		GRAB_POINTER
			Enables wrapping when continuous grab is enabled
		PRESET
			Display a preset button with operator settings
		INTERNAL
			Removes operator from search results
	"""
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR' and context.space_data.image

	def execute(self, context):
		img = context.scene.fave_image_list.add()
		img.image_name = context.space_data.image.name
		return {'FINISHED'}


class FIL_OT_remove_from_faves(Operator):
	"""Removes current image from favorites."""
	bl_idname = "image.fil_ot_remove_from_faves"
	bl_label = "Remove from Fave Images"
	bl_options = {'INTERNAL'}
	
	index : IntProperty(
		name="Index"
	)
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR'

	def execute(self, context):
		context.scene.fave_image_list.remove(self.index)
		return {'FINISHED'}


class FIL_OT_clean_faves(Operator):
	"""Cleans favorites of images that aren't available."""
	bl_idname = "image.fil_ot_clean_faves"
	bl_label = "Clean Fave Images"
	bl_options = {'INTERNAL'}
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR'

	def execute(self, context):
		for index, image in enumerate(context.scene.fave_image_list):
			if image.image_name not in bpy.data.images:
				self.index = index
				FIL_OT_remove_from_faves.execute(self, context)
		return {'FINISHED'}


class FIL_OT_set_current_image(Operator):
	"""Sets current image in current image editor."""
	bl_idname = "image.fil_ot_set_current_image"
	bl_label = "Set Current Image"
	bl_options = {'INTERNAL'}
	
	image_name : StringProperty(
		name="Image Name",
		default=""
	)
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR' and context.scene.fave_image_list

	def execute(self, context):
		if self.image_name in bpy.data.images:
			context.space_data.image = bpy.data.images[self.image_name]
		else:
			print(f"ERROR: {self.image_name} is not in images!")
		return {'FINISHED'}


## UI

class FIL_PT_FaveImagesPanel(bpy.types.Panel):
	"""Fave Images Panel"""
	bl_label = "Favorite Images"
	bl_space_type = 'IMAGE_EDITOR'
	bl_region_type = 'UI'
	bl_category = 'Faves'

	def draw(self, context):
		layout = self.layout
		row = layout.row().split(factor=0.6, align=True)
		row.operator(FIL_OT_add_to_faves.bl_idname)
		row.operator(FIL_OT_clean_faves.bl_idname, text="Clean")
		
		for index, image in enumerate(context.scene.fave_image_list):
			row = layout.row().split(factor=0.9, align=True)
			row.operator(FIL_OT_set_current_image.bl_idname, text=image.image_name).image_name = image.image_name
			row.operator(FIL_OT_remove_from_faves.bl_idname, text="", icon="CANCEL").index = index


## Append to UI Helper Functions

## Register

classes = (
	FaveImageListPropertyGroup,
	FIL_OT_add_to_faves,
	FIL_OT_remove_from_faves,
	FIL_OT_set_current_image,
	FIL_OT_clean_faves,
	FIL_PT_FaveImagesPanel
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.types.Scene.fave_image_list = CollectionProperty(type=FaveImageListPropertyGroup)

def unregister():
	del bpy.types.Scene.fave_image_list
	
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
