using Godot;

public partial class Course : Node3D
{
    [Signal] public delegate void LapCompletedEventHandler(int completedLaps);

    private const float RadiusX = 32f;
    private const float RadiusZ = 52f;
    private const float RoadHalfWidth = 6.7f;

    public int CompletedLaps { get; private set; }
    public int NextCheckpoint { get; private set; }
    public bool RaceActive { get; set; }
    public bool WrongWay { get; private set; }

    private Car car;
    private Area3D[] checkpoints;
    private Transform3D respawn;
    private float wrongWayTime;

    public override void _Ready()
    {
        car = GetNode<Car>("../Car");
        checkpoints = new[] {
            GetNode<Area3D>("North"), GetNode<Area3D>("West"),
            GetNode<Area3D>("South"), GetNode<Area3D>("Finish")
        };
        for (int i = 0; i < checkpoints.Length; i++)
        {
            int index = i;
            checkpoints[i].BodyEntered += body => OnCheckpoint(body, index);
        }
        ResetCourse();
    }

    private void OnCheckpoint(Node3D body, int index)
    {
        if (body != car || !RaceActive || index != NextCheckpoint)
            return;

        Vector3 direction = -checkpoints[index].GlobalBasis.Z;
        if (car.Velocity.Dot(direction) < 0.5f)
            return;

        respawn = checkpoints[index].GlobalTransform;
        respawn.Origin += direction * 5f;
        respawn.Origin = new Vector3(respawn.Origin.X, 0.6f, respawn.Origin.Z);
        NextCheckpoint++;
        if (NextCheckpoint == checkpoints.Length)
        {
            NextCheckpoint = 0;
            CompletedLaps++;
            EmitSignal(SignalName.LapCompleted, CompletedLaps);
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        Vector3 position = car.GlobalPosition;
        Vector3 tangent = new Vector3(RadiusX * position.Z / RadiusZ, 0, -RadiusZ * position.X / RadiusX).Normalized();
        bool backwards = RaceActive && car.Velocity.Dot(tangent) < -2f;
        wrongWayTime = backwards ? wrongWayTime + (float)delta : 0;
        WrongWay = wrongWayTime > 1f;
        if (RaceActive && position.Y < -5)
            RespawnCar();
    }

    public bool IsOnGrass(Vector3 position)
    {
        float angle = Mathf.Atan2(position.Z / RadiusZ, position.X / RadiusX);
        Vector2 roadCenter = new Vector2(RadiusX * Mathf.Cos(angle), RadiusZ * Mathf.Sin(angle));
        return new Vector2(position.X, position.Z).DistanceTo(roadCenter) > RoadHalfWidth;
    }

    public void RespawnCar()
    {
        car.ResetCar(respawn);
        wrongWayTime = 0;
        WrongWay = false;
    }

    public void ResetCourse()
    {
        CompletedLaps = 0;
        NextCheckpoint = 0;
        RaceActive = false;
        WrongWay = false;
        wrongWayTime = 0;
        respawn = GetNode<Marker3D>("Start").GlobalTransform;
    }
}
