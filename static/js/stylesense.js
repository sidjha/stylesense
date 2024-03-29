  var rounds_played = 0;
  var cur_round, prev_round;
  var skipCount = 0;

  initialize();

  function Round(player1, player2) {
    this.player1 = player1;
    this.player2 = player2;
    this.winner = null;

    this.set_winner = function(winner) {
      this.winner = winner;
    }

    this.render = function() {
      setup_players(this.player1, this.player2);
      //$('#photo1').css({'display': 'block'});
      //$('#photo2').css({'display': 'block'});
      $('#photo1').fadeIn();
      $('#metadata1').fadeIn();
      $('#photo2').fadeIn();
      $('#metadata2').fadeIn();
    }

    this.clear_ = function() {
     // $('#photo1').css({'display': 'none'});
     // $('#photo2').css({'display': 'none'});
      $('#photo1').fadeOut();
      $('#metadata1').fadeOut();
      $('#photo2').fadeOut();
      $('#metadata2').fadeOut();
    }

    this.skip = function() {
      $.ajax({
	url: '/skip_round',
	method: 'POST',
	data: {
	  photo1: this.player1.obj_id,
	  photo2: this.player2.obj_id
	}
      });
    }

    this.save = function(obj) {
      $.ajax({
        url: '/tally_round',
        method: 'POST',
        data: {
          photo1: obj.player1.obj_id,
          photo2: obj.player2.obj_id,
          winner: obj.winner.obj_id
        }
      });
    }
  }

  function Player(player) {
    this.image_url = player.image;
    this.link_ = player.link;
    this.net_votes = player.netVotes;
    this.obj_id = player.objectId;
    this.username = player.username;
  }

  function img_error(image) {
    var badPlayer;

    if (cur_round.player1.image_url === image.src) {
      badPlayer = cur_round.player1;
    } else if (cur_round.player2.image_url === image.src) {
      badPlayer = cur_round.player2;
    } else {
      new_round();
      return;
    }

    $.ajax({
      url: '/report_bad_image',
      method: 'POST',
      data: {
        objectId: badPlayer.obj_id
      }
    });

    new_round();
  }

  function new_round() {
    $.ajax({
      url: '/new_round',
      method: 'GET',
      success: function(data) {
        var players = $.parseJSON(data);
        var player1 = new Player(players[0]);
        var player2 = new Player(players[1]);

        cur_round = new Round(player1, player2);
        cur_round.render();
      }
    });
  }

  function initialize() {
    $('#photo1').fadeOut();
    $('#photo2').fadeOut();
    $.ajax({
      url: '/new_round',
      method: 'GET',
      success: function(data) {
        var players = $.parseJSON(data);
        //console.log("Getting initial data...")
        //console.log(players);
        var player1 = new Player(players[0]);
        var player2 = new Player(players[1]);
        cur_round = new Round(player1, player2);
        cur_round.render();
      }
    });
    update_leaderboard();
  }

  function setup_players(player1, player2) {
    $('#photo1').attr('src', player1.image_url)
    $('#photo2').attr('src', player2.image_url)

    $('#user1').html('@' + player1.username).attr('href', 'http://instagram.com/' + player1.username)
    $('#user2').html('@' + player2.username).attr('href', 'http://instagram.com/' + player2.username)

    $('#link1').attr('href', player1.link_)
    $('#link2').attr('href', player2.link_)
  }

  $('#photo1').on('click', function() {
    cur_round.set_winner(cur_round.player1);
    prev_round = cur_round;
    show_results();
    prev_round.clear_();
    new_round();
    prev_round.save(prev_round);
  });

  $('#photo2').on('click', function() {
    cur_round.set_winner(cur_round.player2);
    prev_round = cur_round;
    show_results();
    prev_round.clear_();
    new_round();
    prev_round.save(prev_round);
  });

  $('#skip').on('click', function() {
    cur_round.skip();

    prev_round = cur_round;
    prev_round.clear_();
    new_round();
    skipCount++;

    var round_players = prev_round.player1.obj_id + '&' + prev_round.player2.obj_id;
    ga('send', 'event', 'Round', 'Skipped', round_players, skipCount);
    return false;
  });

  function update_points(points_elem, points) {
    var text = points_elem.parent().find("[id$='text']");
    points_elem.html(points);

    console.log("points; " + points);

    if (points == 1) {
      text.html("point");
    } else {
      text.html("points");
    }
  }

  function show_results() {
  	$('#thumbImg1').attr('src', prev_round.player1.image_url);
  	$('#thumbImg2').attr('src', prev_round.player2.image_url);
  	$('#thumbLink1').attr('href', prev_round.player1.link_);
  	$('#thumbLink2').attr('href', prev_round.player2.link_);
  	$('#thumbUser1').html('@' + prev_round.player1.username).attr('href', 'http://instagram.com/' + prev_round.player1.username);
  	$('#thumbUser2').html('@' + prev_round.player2.username).attr('href', 'http://instagram.com/' + prev_round.player2.username);

        var player1_is_winner = (prev_round.winner.obj_id == prev_round.player1.obj_id);

  	if (player1_is_winner) {
  		$('#result2').removeClass('winner');

  		update_points($('#points1'), prev_round.player1.net_votes + 1);
  		update_points($('#points2'), prev_round.player2.net_votes - 1);

  		$('#result1').addClass('winner');
  	}
  	else {
  		$('#result1').removeClass('winner');

  		update_points($('#points2'), prev_round.player2.net_votes + 1);
  		update_points($('#points1'), prev_round.player1.net_votes - 1);

  		$('#result2').addClass('winner');
  	}
  	$('#score-header').fadeIn();
  	$('#score').fadeIn();
  }

  function Leader(attributes) {
  	this.img_url = attributes['img_url'];
  	this.link_ = attributes['link'];
  	this.username = attributes['username'];
  	this.net_votes = attributes['net_votes'];
  }

  function update_leaderboard() {
  	var leaders = []
  	$.getJSON('/leaderboard', function(data) {
  		for(var i=0; i < data.length; i++) {
  			leaders.push(new Leader(data[i]));
  		}
  		render_leaderboard(leaders);
  	});
  }

  function render_leaderboard(leaders) {
  	$('#leaderboard').empty();
  	for(var i=0; i < leaders.length; i++) {
  		var handle = leaders[i].username;
  		var link = leaders[i].link_;
  		var net_votes = leaders[i].net_votes;
  		var img_url = leaders[i].img_url;
  		li = '<a class="leader_img" href="' + link + '" target="_blank"><img src="' + img_url + '"></a>' +
  			 '<a class="leader_handle" href="http://instagram.com/' + 
  			 handle + '" target="_blank">@' + handle + '</a>' + 
  			 '<span class="stats">' + net_votes + ' points</span>';
  		$('#leaderboard').append('<div class="pure-u-1-5 item">' + li + '</div>');
  	}
  	$('#copyright').css('margin-top', '50px');
  	$('#leaderboard_header').fadeIn();
  	$('#leaderboard').fadeIn();
        $('#see_winners').fadeIn();
  }
