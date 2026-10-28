using Godot;
using System.Diagnostics;

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
	
	//Which book number the player should be on
	public int Book = -1;

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
		Book = -1;
		
		if(Mode != 0){
			var args = "";
			if(Mode == 1)
			{
				args = "/C uv run ../../AI/src/ai/__init__.py";
			}
			else if(Mode == 2)
			{
				args = "/C uv run ../../AI/src/ai/sound_interpreter.py";
			}
			
			try
			{
				Process process = new Process();
				process.StartInfo.FileName = "cmd.exe";
				process.StartInfo.Arguments = args;
				process.StartInfo.CreateNoWindow = false;
				
				process.Start();
			}
			catch (System.Exception e)
			{
				GD.Print(e.ToString());
			}
		}
		
		GetTree().ChangeSceneToFile(Level1);
		StartTime = (double)Time.GetTicksMsec() / 1000.0;
	}

	public void EndGame()
	{
		PlayerWon = true;
		EndTime = (double)Time.GetTicksMsec() / 1000.0;
		TotalTime = EndTime - StartTime;
		
		string FileName = "Results/";
		switch(Mode){
			case 0:
				FileName += "Keyboard.txt";
				break;
			case 1:
				FileName += "Vocal.txt";
				break;
			case 2:
				FileName += "Sound.txt";
				break;
		}
		using var File = FileAccess.Open(FileName, FileAccess.ModeFlags.Write);
		File.StoreString(TotalTime.ToString());
	}
}
