import gs

import particle_emitter
from create_surface import *
import genetique

gs.LoadPlugins()

plus = gs.GetPlus()
plus.CreateWorkers()


plus.RenderInit(1024, 768)

plus.GetRendererAsync().SetVSync(False)

scn = plus.NewScene()
# scn.GetPhysicSystem().SetDebugVisuals(True)

cam = plus.AddCamera(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(0, 1, -10)))
plus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(6, 4, -6)))
plus.AddLight(scn, gs.Matrix4.TranslationMatrix(gs.Vector3(-8, 4, -6)))
plus.AddPhysicPlane(scn)


def add_physic_geo(scn, geo, core_geo, mat=gs.Matrix4.Identity, mass=0, material_path=None):
	"""Create a new plane node, configure its physic attributes, and add it to a scene"""
	node = plus.AddObject(scn, geo, mat)

	rigid_body = gs.MakeRigidBody()
	node.AddComponent(rigid_body)

	collision = gs.MakeMeshCollision()
	collision.SetGeometry(core_geo)
	collision.SetMass(mass)
	node.AddComponent(collision)

	return node, rigid_body

# create the random plane
surface = None

# create the plane to evaluate score
plane, rb_plane = plus.AddPhysicPlane(scn, gs.Matrix4.TransformationMatrix(gs.Vector3(2, 1, -1), gs.Vector3(0.75, 0, 0)), 1, 1)

# initialize particles
particle_emitter.create_particle(scn, 200)

fps = gs.FPSController(0, 2, -10)

# parameters
current_index_tested = 0
duration_test = 4.0
test_timer = 0.0
score = 0.0

while not plus.KeyPress(gs.InputDevice.KeyEscape) and plus.GetRendererAsync().GetDefaultOutputWindow().IsOpen():
	dt_sec = plus.UpdateClock()

	fps.UpdateAndApplyToNode(cam, dt_sec)

	particle_emitter.update(dt_sec.to_sec(), gs.Vector3(2.5, 3, -1), gs.Vector3(-1, 2, 3))

	# test
	# if test timer is under 0, take the next to test
	if test_timer < 0:
		genetique.test_subjects[current_index_tested]["score"] = score
		print("change subject, score {0}, {1} id, {2} test_subjects".format(score, str(current_index_tested + genetique.nb_test_subject*(genetique.current_generation+1)), genetique.current_generation))

		test_timer = duration_test
		score = 0.0
		particle_emitter.deactivate_all_particles()
		# test if need to create a new generation
		current_index_tested += 1
		if current_index_tested >= len(genetique.test_subjects):
			genetique.make_new_generation()
			genetique.current_generation += 1
			current_index_tested = 0

		# remove the geometry and add the new one to test
		scn.RemoveNode(surface)

		core_geo = plus.CreateGeometryFromHeightmap(200, 200, genetique.test_subjects[current_index_tested]["a"].tolist(), 4.0, None, str(current_index_tested + genetique.nb_test_subject * (genetique.current_generation + 1)))
		surface, core_surface = add_physic_geo(scn, gs.GetPlus().CreateGeometry(core_geo, False), core_geo)
	else:
		# count the number of particle colliding
		test_timer -= dt_sec.to_sec()

	if scn.GetPhysicSystem().HasCollided(plane):
		score += 1

	plus.UpdateScene(scn, dt_sec)
	plus.Text2D(5, 5, "Move around with QSZD, left mouse button to look around")
	plus.Flip()