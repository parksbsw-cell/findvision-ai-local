from app.providers.diffusers_local import LocalImageGenerator


def test_pose_template_matches_gender_and_child_age():
    assert LocalImageGenerator._pose_path("gender: male; age: 40").name == "neutral-front-pose-v2.png"
    assert LocalImageGenerator._pose_path("gender: female; age: 72").name == "neutral-front-female.png"
    assert LocalImageGenerator._pose_path("gender: male; age: 9").name == "neutral-front-boy.png"
    assert LocalImageGenerator._pose_path("gender: female; age: 9").name == "neutral-front-girl.png"
