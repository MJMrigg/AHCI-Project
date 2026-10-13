using Godot;
using System;

public partial class FireWizard : CharacterBody2D
{
	[Export] public CollisionShape2D MyPhyCol; // Don't know if this will be needed yet. Here just in case - David T
	[Export] public AnimatedSprite2D MySpriteAnim; 
	
	[Export] public int Speed = 200; //How fast the character should move

	public override void _PhysicsProcess(double delta)
	{
		base._PhysicsProcess(delta);

		// returns vector with max length of one
		Vector2 move_direction = Input.GetVector("Left", "Right", "Up", "Down");

		if(move_direction.IsZeroApprox()){
			MySpriteAnim.Animation = "Idle";
		}
		else{
			MySpriteAnim.Animation = "Walk";
		}

		if(move_direction.X > 0){
			MySpriteAnim.FlipH = false;
		}
		else if(move_direction.X < 0){
			MySpriteAnim.FlipH = true;
		}

		Velocity = move_direction.Normalized() * Speed;
		
		MoveAndSlide();
	}
}
