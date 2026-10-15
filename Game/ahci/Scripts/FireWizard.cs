using Godot;
using System;

public partial class FireWizard : CharacterBody2D
{
	[Export] public CollisionShape2D MyPhyCol; // Don't know if this will be needed yet. Here just in case - David T
	[Export] public AnimatedSprite2D MySpriteAnim;
	
	[Export] public int Speed = 200; //How fast the character should move

	[Export] private Area2D _interactArea;
	[Export] private PackedScene _fireball_scene;
	[Export] private Node2D _fireball_spawnpoint_r;
	[Export] private Node2D _fireball_spawnpoint_l;

	public override void _UnhandledInput(InputEvent @event)
	{
		base._UnhandledInput(@event);

		if(@event.IsActionPressed("fireball"))
		{
			MySpriteAnim.Play("Fireball");
		}
		else if(@event.IsActionPressed("interact"))
		{
			foreach(var area in _interactArea.GetOverlappingAreas())
			{
				// TODO: add once IInteractable is added
				// if(area is IInteractable interactable){
				// 	interactable.interact();
				// }
			}
		}
		else if(@event.IsActionPressed("wind"))
		{
			// TODO: wind effect
		}
	}

	public override void _PhysicsProcess(double delta)
	{
		base._PhysicsProcess(delta);

		// returns vector with max length of one
		Vector2 move_direction = Input.GetVector("Left", "Right", "Up", "Down");

		if(move_direction.X > 0)
		{
			MySpriteAnim.FlipH = false;
		}
		else if(move_direction.X < 0)
		{
			MySpriteAnim.FlipH = true;

		}


		// quick and dirty state machine using animation
		// to determine current state
		switch (MySpriteAnim.Animation)
		{
			case "Idle":
			case "Walk":
				MySpriteAnim.Animation = move_direction.IsZeroApprox() ? "Idle" : "Walk";
				if(Input.IsActionJustPressed("fireball"))
				{
					// MySpriteAnim.Play("Fireball");
				}
				break;
			case "Fireball":
				break;
		}

		Velocity = move_direction.Normalized() * Speed;

		MoveAndSlide();
	}

	private void ShootFireball()
	{
		FireBall new_fireball = _fireball_scene.Instantiate<FireBall>();
		var spawnpoint = MySpriteAnim.FlipH ? _fireball_spawnpoint_l : _fireball_spawnpoint_r;
		new_fireball.GlobalPosition = spawnpoint.GlobalPosition;
		new_fireball.GlobalRotation = MySpriteAnim.FlipH ? Mathf.Pi : 0;
		// GetParent().AddChild(new_fireball);
		GetParent().CallDeferred(MethodName.AddChild, new_fireball);
	}

	private void OnAnimationFinished()
	{
		// only fired when non-looping animations finish
		// so idle and walk won't trigger this
		if(MySpriteAnim.Animation == "Fireball"){
			ShootFireball();
		}
		
		MySpriteAnim.Play("Idle");
	}
}
