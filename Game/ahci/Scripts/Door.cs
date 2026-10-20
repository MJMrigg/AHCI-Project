using Godot;
using System;

public partial class Door : Area2D
{
	
	[Export] public string NextRoom;
	
	//Go through the door to the next scene
	public async void GoThrough()
	{
		if(NextRoom != null)
		{
			GetTree().ChangeSceneToFile(NextRoom);
		}
	}
	
	private void OnBodyEnter(Node2D body)
	{
		if(body is FireWizard)
		{
			CallDeferred(nameof(GoThrough));
		}
	}
	
	
}
