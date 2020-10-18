import unreal
#Spawn Actor
#Video:https://www.youtube.com/watch?v=UGnbx7iNMBQ
actor_location = unreal.Vector(0,0,0)
actor_rotation = unreal.Rotator(0,0,0)
actor_class = unreal.EditorAssetLibrary.load_blueprint_class('/Game/Blueprints/BPAviao')
unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class,actor_location,actor_rotation)


