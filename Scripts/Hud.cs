using Godot;

public partial class Hud : Control
{
    private const float DialMaximumSpeed = 160f;
    private const float DialStartAngle = 140f;
    private const float DialEndAngle = 400f;

    private Label speedLabel;
    private Label lapLabel;
    private Label timeLabel;
    private Label lapTimeLabel;
    private Label warning;
    private Control countdown;
    private Control menu;
    private Control needleOverlay;
    private float speed;
    private readonly Color cream = new Color("f1eedb");
    private readonly Color gold = new Color("f7b747");
    private readonly Color muted = new Color("678089");

    public override void _Ready()
    {
        speedLabel = GetNode<Label>("Speed");
        lapLabel = GetNode<Label>("Lap");
        timeLabel = GetNode<Label>("Time");
        lapTimeLabel = GetNode<Label>("LapTime");
        warning = GetNode<Label>("WrongWay");
        countdown = GetNode<Control>("Countdown");
        menu = GetNode<Control>("Menu");
        needleOverlay = GetNode<Control>("Needle");
        needleOverlay.Draw += DrawNeedle;
    }

    public void UpdateRace(Car car, int lap, float time, float lapTime, bool wrongWay)
    {
        speed = car.SpeedKmh;
        speedLabel.Text = Mathf.RoundToInt(speed).ToString("000");
        lapLabel.Text = $"{lap} / {Game.TotalLaps}";
        timeLabel.Text = FormatTime(time);
        lapTimeLabel.Text = $"LAP  {FormatTime(lapTime)}";
        warning.Visible = wrongWay;
        QueueRedraw();
        needleOverlay.QueueRedraw();
    }

    private static string FormatTime(float seconds)
    {
        int hundredths = (int)(seconds * 100);
        return $"{hundredths / 6000:00}:{hundredths / 100 % 60:00}.{hundredths % 100:00}";
    }

    public void ShowCountdown(string text)
    {
        countdown.Visible = true;
        countdown.GetNode<Label>("Number").Text = text;
    }

    public void HideCountdown() => countdown.Visible = false;
    public void HideMenu() => menu.Visible = false;

    public void ShowMenu(bool won, float time, float best)
    {
        menu.Visible = true;
        menu.GetNode<Label>("Panel/Title").Text = won ? "GOAL!" : "PAUSED";
        menu.GetNode<Label>("Panel/Result").Text = $"RACE  {FormatTime(time)}\nBEST LAP  {(best > 0 ? FormatTime(best) : "--:--.--")}";
        Button resume = menu.GetNode<Button>("Panel/Resume");
        resume.Visible = !won;
        (won ? menu.GetNode<Button>("Panel/RaceAgain") : resume).GrabFocus();
    }

    public override void _Draw()
    {
        Vector2 dial = new Vector2(Size.X - 134, Size.Y - 130);
        DrawCircle(dial, 100, new Color("142c36ed"));
        float start = Mathf.DegToRad(DialStartAngle);
        float end = Mathf.DegToRad(DialEndAngle);
        DrawArc(dial, 88, start, end, 64, muted, 5, true);
        DrawArc(dial, 88, start, Mathf.Lerp(start, end, Mathf.Clamp(speed / DialMaximumSpeed, .001f, 1)), 64, gold, 5, true);
        for (int i = 0; i <= 12; i++)
        {
            float angle = Mathf.Lerp(start, end, i / 12f);
            Vector2 direction = Vector2.FromAngle(angle);
            DrawLine(dial + direction * 73, dial + direction * (i % 3 == 0 ? 83 : 79), cream, 2, true);
        }
    }

    private void DrawNeedle()
    {
        Vector2 dial = new Vector2(Size.X - 134, Size.Y - 130);
        float start = Mathf.DegToRad(DialStartAngle);
        float end = Mathf.DegToRad(DialEndAngle);
        Vector2 needle = Vector2.FromAngle(Mathf.Lerp(start, end, Mathf.Clamp(speed / DialMaximumSpeed, 0, 1)));
        Vector2 pivot = dial + new Vector2(0, 48);
        needleOverlay.DrawLine(pivot, pivot + needle * 62, gold, 4, true);
        needleOverlay.DrawCircle(pivot, 5, gold);
    }
}
