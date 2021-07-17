bl_info = {
	"name": "Favorite Image List",
	"author": "Kenetics",
	"version": (0, 2),
	"blender": (2, 90, 0),
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
	image : PointerProperty(type = bpy.types.Image)


## Operators

class FIL_OT_add_to_faves(Operator):
	"""Adds current image to favorites."""
	bl_idname = "image.fil_ot_add_to_faves"
	bl_label = "Add to Fave Images"
	bl_options = {'INTERNAL'}

	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR' and context.space_data.image

	def execute(self, context):
		new_fave_image = context.scene.fave_image_list.add()
		new_fave_image.image = context.space_data.image
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
		for index, fave_image in enumerate(context.scene.fave_image_list):
			if not fave_image.image:
				self.index = index
				FIL_OT_remove_from_faves.execute(self, context)
		return {'FINISHED'}


class FIL_OT_set_current_image(Operator):
	"""Sets current image in current image editor."""
	bl_idname = "image.fil_ot_set_current_image"
	bl_label = "Set Current Image"
	bl_options = {'INTERNAL'}
	
	index : IntProperty(
		name="Index"
	)
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'IMAGE_EDITOR' and context.scene.fave_image_list

	def execute(self, context):
		fave_image = context.scene.fave_image_list[self.index]
		if fave_image.image:
			context.space_data.image = fave_image.image
		else:
			print(f"ERROR: This image is not in images!")
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
		row = layout.split(factor=0.6, align=True)
		row.operator(FIL_OT_add_to_faves.bl_idname)
		row.operator(FIL_OT_clean_faves.bl_idname, text="Clean")
		
		for index, fave_image in enumerate(context.scene.fave_image_list):
			if fave_image.image:
				row = layout.split(factor=0.9, align=True)
				row.operator(FIL_OT_set_current_image.bl_idname, text=fave_image.image.name).index = index
				row.operator(FIL_OT_remove_from_faves.bl_idname, text="", icon="CANCEL").index = index
			else:
				row = layout.row()
				row.operator(FIL_OT_remove_from_faves.bl_idname, text="BROKEN IMAGE", icon="CANCEL").index = index


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
