using Godot;
using System;
using System.Diagnostics;

public partial class MainMenu : Control
{
	[Export] public bool HideDebugConsole;
	
	public void play(){
		GetTree().ChangeSceneToFile("uid://cuuimd7fyr2kj");
	}
	
	public void keyboard(){
		//Change mode in singleton
		play();
	}
	
	public void vocal(){
		//Change mode in singleton
		startProcess("/C uv run ../../AI/src/ai/__init__.py");
		play();
	}
	
	public void sound(){
		//Change mode in singleton
		startProcess("/C uv run ../../AI/src/ai/sound_interpreter.py");
		play();
	}
	
	public void startProcess(string args)
	{
		try
		{
			Process process = new Process();
			process.StartInfo.FileName = "cmd.exe";
			process.StartInfo.Arguments = args;
			process.StartInfo.CreateNoWindow = HideDebugConsole;
			
			process.Start();
		}
		catch (System.Exception e)
		{
			GD.Print(e.ToString());
		}
	}
}
