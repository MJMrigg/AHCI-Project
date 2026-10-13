using Godot;
using System;

public partial class PauseMenu : ColorRect
{
	public void Yes(){
		if(GetTree().GetCurrentScene().Name == "MainMenu")
		{
			GetTree().Quit();
		}
		GetTree().ChangeSceneToFile("uid://dcsoxuw8fc8fk");
	}
	
	public void No(){
		Hide();
	}
	
	public void Reveal(){
		if(Visible)
		{
			Hide();
		}
		else
		{
			Show();
		}
	}
}
