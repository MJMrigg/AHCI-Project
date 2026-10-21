using Godot;
using System;

public partial class EndMenu : ColorRect
{
	public void End()
	{
		if(GetTree().GetCurrentScene().Name == "MainMenu")
		{
			GetTree().Quit();
		}
		GetTree().ChangeSceneToFile("uid://dcsoxuw8fc8fk");
	}
}
