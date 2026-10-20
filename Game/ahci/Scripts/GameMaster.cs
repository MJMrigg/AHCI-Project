using Godot;

public partial class GameMaster : Node
{
	public static GameMaster Instance { get; set; }

	[Export]
	private string Level1 = "uid://cuuimd7fyr2kj";

	// The mode the player is playing in
	public int Mode = 0;

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
	
	// Start the game in sound mode
	public void StartSound()
	{
		Mode = 2;
		BeginGame();
	}

	// Start the game in vocal mode
	public void StartVocal()
	{
		Mode = 1;
		BeginGame();
	}

	// Start the game in keyboard mode
	public void StartKeyboard()
	{
		Mode = 0;
		BeginGame();
	}

	// Switch to the first scene
	public void BeginGame()
	{
		PlayerWon = false;
		GetTree().ChangeSceneToFile(Level1);
		StartTime = (double)Time.GetTicksMsec() / 1000.0;
	}

	public void EndGame()
	{
		PlayerWon = true;
		EndTime = (double)Time.GetTicksMsec() / 1000.0;
		TotalTime = EndTime - StartTime;
	}
}
