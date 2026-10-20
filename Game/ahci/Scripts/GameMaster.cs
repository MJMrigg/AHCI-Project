using Godot;

public partial class GameMaster : Node
{
	public static GameMaster Instance { get; set; }

    [Export]
    private PackedScene Level1;

    // Whether the player is using audio mode or not
    public bool AudioMode = false;

    // Whether the player has won the game
    public bool PlayerWon = false;

	public double StartTime = 0.0f;
    public double EndTime = 0.0f;
    public double TotalTime = 0.0f;

    public override void _Ready()
    {
        base._Ready();
        Instance = this;
    }

    // Start the game in audio mode
    public void StartAudio()
    {
        AudioMode = true;
        BeginGame();
    }

    // Start the game in keyboard mode
    public void StartKeyboard()
    {
        AudioMode = false;
        BeginGame();
    }

    // Switch to the first scene
    public void BeginGame()
    {
        PlayerWon = false;
        GetTree().ChangeSceneToPacked(Level1);
        StartTime = (double)Time.GetTicksMsec() / 1000.0;
    }

	public void EndGame()
    {
        PlayerWon = true;
        EndTime = (double)Time.GetTicksMsec() / 1000.0;
        TotalTime = EndTime - StartTime;
    }
}
