using Godot;
using System;

public partial class Chest : Area2D
{
	[Export] public ColorRect endMenu;
	
	private void OnBodyEnter(Node2D body)
	{
		//If the player found the chest, win the game
		if (body is FireWizard)
		{
			// UI Element for win does not exist yet.
			// TODO Reveal UI once completed
			GameMaster.Instance.EndGame();
			endMenu.Show();
		}

		
	}
}
