using Godot;

public partial class Car : CharacterBody3D
{
	[Export] public float MaxSpeed = 30f;
	[Export] public float BoostSpeed = 42f;
	[Export] public float Acceleration = 13f;
	[Export] public float SteeringSpeed = 1.65f;

	public bool CanDrive { get; set; }
	public float SpeedKmh => new Vector2(Velocity.X, Velocity.Z).Length() * 3.6f;

	private const float BrakeDeceleration = 34f;
	private const float WheelRadius = 0.43f;
	private const float CameraDistance = 8f;
	private const float CameraHeight = 4.6f;
	private const float CameraFov = 65f;

	private float speed;
	private float steering;
	private Vector3 horizontalVelocity;
	private Node3D body;
	private Node3D[] wheelPivots;
	private Node3D[] wheels;
	private Camera3D camera;
	private float wheelSpin;
	private Course course;

	public override void _Ready()
	{
		body = GetNode<Node3D>("Body");
		camera = GetNode<Camera3D>("Camera3D");
		course = GetNode<Course>("../Course");
		wheelPivots = new[] {
			GetNode<Node3D>("FrontLeft"), GetNode<Node3D>("FrontRight"),
			GetNode<Node3D>("RearLeft"), GetNode<Node3D>("RearRight")
		};
		wheels = new Node3D[4];
		for (int i = 0; i < 4; i++)
			wheels[i] = wheelPivots[i].GetNode<Node3D>("Wheel");
		ResetCar(GlobalTransform);
	}

	public override void _PhysicsProcess(double delta)
	{
		float dt = (float)delta;
		float throttle = CanDrive ? Input.GetAxis("reverse", "accelerate") : 0;
		float turn = CanDrive ? Input.GetAxis("steer_left", "steer_right") : 0;
		bool braking = CanDrive && Input.IsActionPressed("handbrake");
		steering = Mathf.MoveToward(steering, turn, dt * 5f);

		bool onGrass = course.IsOnGrass(GlobalPosition);
		bool boosting = CanDrive && throttle > 0 && !braking && !onGrass && Input.IsActionPressed("boost");
		float limit = onGrass ? 9f : (boosting ? BoostSpeed : MaxSpeed);
		float acceleration = boosting ? Acceleration * 1.6f : Acceleration;

		if (!CanDrive || braking)
			speed = Mathf.MoveToward(speed, 0, BrakeDeceleration * dt);
		else if (throttle > 0)
			speed = Mathf.MoveToward(speed, limit * throttle, acceleration * dt);
		else if (throttle < 0)
			speed = Mathf.MoveToward(speed, 8f * throttle, (speed > 0 ? 22f : 9f) * dt);
		else
			speed = Mathf.MoveToward(speed, 0, 4f * dt);

		MoveCar(dt, braking);
		AnimateWheels(dt);
	}

	private void MoveCar(float dt, bool braking)
	{
		float turnAmount = Mathf.Clamp(Mathf.Abs(speed) / 9f, 0, 1);
		RotateY(-steering * SteeringSpeed * turnAmount * Mathf.Sign(speed) * dt);
		Vector3 forward = -GlobalBasis.Z;
		if (braking || !CanDrive)
			horizontalVelocity = horizontalVelocity.MoveToward(Vector3.Zero, BrakeDeceleration * dt);
		else
			horizontalVelocity = horizontalVelocity.Lerp(forward * speed, Mathf.Min(9f * dt, 1));
		Velocity = new Vector3(horizontalVelocity.X, IsOnFloor() ? -0.5f : Velocity.Y - 22f * dt, horizontalVelocity.Z);
		MoveAndSlide();

		for (int i = 0; i < GetSlideCollisionCount(); i++)
		{
			if (Mathf.Abs(GetSlideCollision(i).GetNormal().Y) < 0.5f)
			{
				speed *= 0.75f;
				horizontalVelocity = new Vector3(Velocity.X, 0, Velocity.Z);
				break;
			}
		}
	}

	private void AnimateWheels(float dt)
	{
		wheelSpin -= speed * dt / WheelRadius;
		for (int i = 0; i < 4; i++)
		{
			wheelPivots[i].Rotation = new Vector3(0, i < 2 ? -steering * 0.42f : 0, 0);
			wheels[i].Rotation = new Vector3(wheelSpin, 0, 0);
		}
		body.Rotation = new Vector3(0, 0, steering * Mathf.Min(Mathf.Abs(speed) / MaxSpeed, 1) * 0.055f);
	}

	public override void _Process(double delta)
	{
		Vector3 target = GlobalPosition + GlobalBasis.Z * CameraDistance + Vector3.Up * CameraHeight;
		camera.GlobalPosition = camera.GlobalPosition.Lerp(target, 1 - Mathf.Exp(-7f * (float)delta));
		camera.LookAt(GlobalPosition - GlobalBasis.Z * 3f + Vector3.Up * 0.6f);
		camera.Fov = Mathf.Lerp(camera.Fov, CameraFov + SpeedKmh * 0.055f, (float)delta * 3f);
	}

	public void ResetCar(Transform3D spawn)
	{
		GlobalTransform = spawn;
		Velocity = Vector3.Zero;
		horizontalVelocity = Vector3.Zero;
		speed = 0;
		steering = 0;
		wheelSpin = 0;
		body.Rotation = Vector3.Zero;
		for (int i = 0; i < 4; i++)
		{
			wheelPivots[i].Rotation = Vector3.Zero;
			wheels[i].Rotation = Vector3.Zero;
		}
		camera.GlobalPosition = GlobalPosition + GlobalBasis.Z * CameraDistance + Vector3.Up * CameraHeight;
		camera.LookAt(GlobalPosition - GlobalBasis.Z * 3f + Vector3.Up * 0.6f);
		camera.Fov = CameraFov;
	}
}
