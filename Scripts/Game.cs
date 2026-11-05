using Godot;

public partial class Game : Node3D
{
	public const int TotalLaps = 3;

	private Car car;
	private Course course;
	private Hud hud;
	private float countdown;
	private float raceTime;
	private float lapTime;
	private float bestLap;
	private float goTime;
	private bool racing;
	private bool finished;
	private bool paused;

	public override void _Ready()
	{
		ProcessMode = ProcessModeEnum.Always;
		car = GetNode<Car>("Car");
		course = GetNode<Course>("Course");
		hud = GetNode<Hud>("Interface/Hud");
		course.LapCompleted += OnLapCompleted;
		hud.GetNode<Button>("Menu/Panel/RaceAgain").Pressed += StartRace;
		hud.GetNode<Button>("Menu/Panel/Resume").Pressed += TogglePause;
		hud.GetNode<Button>("Menu/Panel/Exit").Pressed += () => GetTree().Quit();
		StartRace();
	}

	public void StartRace()
	{
		GetTree().Paused = false;
		paused = false;
		racing = false;
		finished = false;
		countdown = 3f;
		raceTime = 0;
		lapTime = 0;
		bestLap = 0;
		goTime = 0;
		course.ResetCourse();
		car.CanDrive = false;
		course.RespawnCar();
		hud.HideMenu();
		hud.ShowCountdown("3");
		hud.UpdateRace(car, 1, 0, 0, false);
	}

	public override void _Process(double delta)
	{
		if (paused)
			return;

		float dt = (float)delta;
		if (countdown > 0)
		{
			countdown -= dt;
			if (countdown <= 0)
			{
				racing = true;
				car.CanDrive = true;
				course.RaceActive = true;
				goTime = 0.8f;
				hud.ShowCountdown("GO!");
			}
			else
				hud.ShowCountdown(Mathf.CeilToInt(countdown).ToString());
		}
		else if (racing)
		{
			raceTime += dt;
			lapTime += dt;
			if (goTime > 0)
			{
				goTime -= dt;
				if (goTime <= 0)
					hud.HideCountdown();
			}
		}

		hud.UpdateRace(car, Mathf.Min(course.CompletedLaps + 1, TotalLaps), raceTime, lapTime, course.WrongWay);
	}

	private void OnLapCompleted(int completed)
	{
		if (!racing)
			return;
		if (bestLap == 0 || lapTime < bestLap)
			bestLap = lapTime;
		lapTime = 0;
		if (completed < TotalLaps)
			return;

		racing = false;
		finished = true;
		course.RaceActive = false;
		car.CanDrive = false;
		hud.HideCountdown();
		hud.ShowMenu(true, raceTime, bestLap);
	}

	public override void _UnhandledInput(InputEvent input)
	{
		if (input.IsActionPressed("pause") && !finished)
		{
			TogglePause();
			GetViewport().SetInputAsHandled();
		}
		if (input.IsActionPressed("reset_car") && racing && !paused)
			course.RespawnCar();
	}

	private void TogglePause()
	{
		if (finished)
			return;
		paused = !paused;
		GetTree().Paused = paused;
		if (paused)
			hud.ShowMenu(false, raceTime, bestLap);
		else
			hud.HideMenu();
	}
}
