using Godot;
using System;

public partial class FireWizard : CharacterBody2D
{
	[Export] public CollisionShape2D MyPhyCol; // Don't know if this will be needed yet. Here just in case - David T
	[Export] public AnimatedSprite2D MySpriteAnim; 
	
	[Export] public int Speed = 200; //How fast the character should move
	
	public override void _Ready()
	{
		base._Ready();
		MySpriteAnim.Animation = "Idle";
	}
	
	public override void _Process(double delta)
	{
		base._Process(delta);
		
		// --- Player Movement ---
		//Get player input 
		float hInput = Input.GetAxis("Left", "Right");
		float vInput = Input.GetAxis("Down", "Up");
		Velocity = new Vector2(0,0);
		//Determine Velocity
		if (Mathf.Abs(hInput) < 0.1f && Mathf.Abs(vInput) < 0.1f)
		{ //If the velocity is 0 (no movement) play idel
			MySpriteAnim.Animation = "Idle";
		}
		else if (Mathf.Abs(hInput) >= Mathf.Abs(vInput))
		{
			//If the player is moving left or right
			if (hInput > 0)
			{ //If the player is moving right
				Velocity += new Vector2(Speed, 0);
				MySpriteAnim.Animation = "Walk";
			}
			else
			{ 
				//If the player is moving left
				Velocity += new Vector2(-Speed, 0);
				MySpriteAnim.Animation = "Walk"; // TODO Add left walk anim
			}
			//If the player is walking diagonally
			if(Mathf.Abs(hInput) == Mathf.Abs(vInput))
			{
				if(vInput > 0)
				{ 
					//Diagonally Up
					Velocity += new Vector2(0,-Speed);
				}
				else
				{
					//Diagonally Down
					Velocity += new Vector2(0,Speed);
				}
				//Adjust using the unit circle so that diagonal movement isn't faster
				float Adjustment = Mathf.Sqrt(2)/2;
				Velocity *= new Vector2(Adjustment,Adjustment);
			}
		}
		else
		{ //If the player is moving up or down
			if (vInput > 0)
			{
				//up
				Velocity += new Vector2(0, -Speed);
				// No Up animation
			}
			else
			{
				//down
				Velocity += new Vector2(0, Speed);
				// No Down Animation
			}
		}
		
		MySpriteAnim.Play();
		MoveAndSlide();
	}
	
}
