from django.db import models
import requests,datetime
from slugify import slugify
from pprint import pprint


# Create your models here.
class Champion(models.Model):
	"""docstring for Champion Remi"""
	championId = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=30)
	def __str__(self):
		return self.name
	"""Ajout stat base champion"""



class Team(models.Model):
	name = models.CharField(max_length=30)
    #Modification Remi
	def __str__(self):
		return self.name

	def getWins(self,win):
		return self.side_set.filter(win=win)

	def getNumberOfPlayedGame(self):
		return self.side_set.all().count()

	def getNumberOfWin(self):
		return len(self.getWins(True))

class Player(models.Model):
	name = models.CharField(max_length = 30)
	summonerId = models.CharField(max_length = 30, blank=True,null=True)
	accountId = models.CharField(max_length = 30, primary_key=True)
	slug = models.CharField(max_length = 30, blank=True,null=True)
        #Changement ELias
	def __str__(self):
		return self.name
	def getWins(self,win):
		return list(filter(lambda x: x.side.win == win,self.playerstats_set.all()))

	def getNumberOfPlayedGame(self):
		return self.played.all().count()

	def getNumberOfWin(self):
		return len(self.getWins(True))

	def createSlug(self):
		self.slug = slugify(self.name)

class Gear(models.Model):
	#STAT_TYPE = [
	#('FMSP','FlatMovementSpeedMod'),
	#('FHPPM','FlatHPPoolMod'),
	#('FCCM','FlatCritChanceMod'),
	#('FMDM','FlatMagicDamageMod'),
	#('FMPPM','FlatMPPoolMod'),
	#('FAM','FlatArmorMod',)
	#('FSBM','FlatSpellBlockMod'),
	#('FPDM','FlatPhysicalDamageMod'),
	#('PASM','PercentAttackSpeedMod'),
	#('PLSM','PercentLifeStealMod'),
	#('FHPRM','FlatHPRegenMod'),
	#('PMSM','PercentMovementSpeedMod'),
	#('FMPRM','FlatMPRegenMod'),
	#]

	FlatMovementSpeedMod = models.IntegerField(blank=True,null=True)
	FlatHPPoolMod = models.IntegerField(blank=True,null=True)
	FlatCritChanceMod = models.IntegerField(blank=True,null=True)
	FlatMagicDamageMod = models.IntegerField(blank=True,null=True)
	FlatMPPoolMod = models.IntegerField(blank=True,null=True)
	FlatArmorMod = models.IntegerField(blank=True,null=True)
	FlatSpellBlockMod = models.IntegerField(blank=True,null=True)
	FlatPhysicalDamageMod = models.IntegerField(blank=True,null=True)
	PercentAttackSpeedMod = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
	PercentLifeStealMod = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
	FlatHPRegenMod = models.IntegerField(blank=True,null=True)
	PercentMovementSpeedMod = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)
	FlatMPRegenMod = models.IntegerField(blank=True,null=True)

	gearId = models.IntegerField(primary_key=True)
	name = models.CharField( max_length = 80 )
	def __str__(self):
		return self.name

class Timestamp(models.Model):
	timestamp = models.TimeField()

class Match(models.Model):
	gameId= models.IntegerField(primary_key=True)
	platformId = models.CharField(max_length=15,blank=True,null=True)
	seasonId= models.IntegerField(blank=True,null=True)
	queueId= models.IntegerField(blank=True,null=True)
	gameCreation= models.DateField(blank=True,null=True)
	duration = models.DurationField(blank=True,null=True)
	gameHash = models.CharField(max_length=100,blank=True,null=True)
	teams = models.ManyToManyField(Team, 
		through='Side',
		through_fields=('match', 'team'),
		)

	def importFromRiot(self):
		gameHash ='0d4877e106c62e79&fbclid=IwAR0Hm1AghOWJHblxxe-cJ5Q0hdfyMn4QYSXwqaaQy5i6V5RvDLknDOTCalw'
		url_match = "https://acs.leagueoflegends.com/v1/stats/game/%s/%s?gameHash=%s" % (self.platformId,self.gameId,self.gameHash)
		url_timeline = "https://acs.leagueoflegends.com/v1/stats/game/%s/%s/timeline?gameHash=%s" % (self.platformId,self.gameId,self.gameHash)
		#url_match = "https://%s.api.riotgames.com/lol/match/v4/timelines/by-match/%s?api_key=%s" % ('Realm',self.gameId,'RestAp')
		try:
			r = requests.get(url_match)
			r2 = requests.get(url_timeline)

		except:
			pass
		data = r.json()
		data_timeline = r2.json()
		game = self
		#,seasonId=data['seasonId'],queueId=data['queueId']
		self.seasonId=data['seasonId']
		self.queueId=data['queueId']
		self.platformId=data['platformId']
		self.duration = datetime.timedelta(seconds=data['gameDuration'])
		self.gameCreation = datetime.datetime.fromtimestamp(int(int(data['gameCreation'])/1000)) #TimeStamp in milliseconde
		self.save()
		particpants = {}
		playserstats = {}
		teams = {}
		
		####### Importation des Sides 
		for team in data['teams']:
			if team['teamId'] == 100:
				side = Side.objects.get_or_create(match=game,side='B')[0]
				teams[100] = side
				side.teamId = 100
			else:
				side = Side.objects.get_or_create(match=game,side='R')[0]
				teams[200] = side
				side.teamId = 200
			if team['win'] == 'Win':
				side.win = True
			else:
				 side.false = True
			for ban in team['bans']:
				try:
					b = Champion.objects.get(championId=ban['championId'])
					side.bans.add(b)
				except:
					pass
			side.save()
		
		#### Importation des Participants
		for participant in data['participantIdentities']:
			particpants[participant['participantId']] = Player.objects.update_or_create(
				name=participant['player']['summonerName'],
				accountId=participant['player'].get('accountId',participant['player']['summonerName']),
				summonerId=participant['player'].get('summonerId',participant['player']['summonerName']),
				)[0]
		
		for participant in data['participants']:
			playerstat = PlayerStats.objects.get_or_create(player=particpants[participant['participantId']], side = teams[participant['teamId']] )[0]
			
			try:
				playerstat.champion = Champion.objects.get_or_create(championId = participant['championId'])[0]
			except:
				print("error finding champion by ID : %s" % participant['championId'] )
			playerstat.kills = participant['stats']['kills']
			playerstat.assists = participant['stats']['assists']
			playerstat.deaths = participant['stats']['deaths']
			playerstat.participantId = participant['participantId']
			playerstat.save()
			playserstats[participant['participantId']] = playerstat


		#### Import Event
		for frame in data_timeline['frames']:
			
			for key,participantFrame in frame['participantFrames'].items():
				ts = TimestampStats.objects.get_or_create(playerstat=playserstats[participantFrame['participantId']], timestamp=frame['timestamp'] )[0]
				ts.currentGold = participantFrame.get('currentGold')
				ts.totalGold = participantFrame['totalGold']
				ts.level = participantFrame['level']
				ts.xp = participantFrame['xp']
				ts.minionsKilled = participantFrame['minionsKilled']
				ts.jungleMinionsKilled = participantFrame['jungleMinionsKilled']
				#ts.dominionScore = participantFrame['dominionScore']
				ts.save()

		

			for event in frame['events']:
				p_id = event.get('participantId',
					event.get('killerId',
						event.get('creatorId',False)
						)
					)
				if p_id != 0:
					try:
						ev = Event.objects.get_or_create(playerstat=playserstats[p_id], timestamp=event['timestamp'], eventType=event['type'] )[0]
					except Exception as e:
						pprint(event)
					
				elif event.get('teamId',False):
					ev = Event.objects.get_or_create(side=teams[event['teamId'] ] , timestamp=event['timestamp'], eventType=event['type'] )[0]
				
				ev.UpdateEvent(event)
				if event['type'] == 'CHAMPION_KILL':
					for assist in event['assistingParticipantIds']:
						ev.assistingParticipants.add(playserstats[assist])
					ev.victim = playserstats[event['victimId']]
				ev.save()
		


	def __str__(self):
		return "Game {0} of Realm {1} ".format(self.gameId,self.platformId)




class Side(models.Model):
	win = models.BooleanField(default=False)
	SIDE_COLOR = [('R','Red'), 
				 ('B','Blue')]
	side = models.CharField(max_length = 10, choices = SIDE_COLOR)
	teamId = models.PositiveIntegerField(blank=True,null=True)
	match = models.ForeignKey(
		Match,
		on_delete=models.CASCADE,
	)
	team = models.ForeignKey(
		Team,
		on_delete=models.CASCADE,blank=True,null=True
	)
	players = models.ManyToManyField(Player, 
		through='PlayerStats',
		through_fields=('side', 'player'),
		related_name='played'
		)

	bans = models.ManyToManyField(Champion,related_name='bans')

	class Meta:
		unique_together = (('match', 'side'),)

	def __str__(self):
		return "{0} Team from {1}".format(self.side, self.match)




class PlayerStats(models.Model):
	ROLE_TYPE = [
	('TOP', 'TOP'),
	('JUNGLE', 'JUNGLE'),
	('MIDDLE', 'MIDDLE'),
	('AD_CARRY', 'AD_CARRY'),
	('SUPPORT', 'SUPPORT'),
	]
	participantId = models.IntegerField(blank=True,null=True)
	kills = models.IntegerField(blank=True,null=True)
	assists = models.IntegerField(blank=True,null=True)
	deaths = models.IntegerField(blank=True,null=True)
	role = models.CharField(max_length = 30, choices = ROLE_TYPE,blank=True,null=True)
	champion =  models.ForeignKey(
		Champion,
		on_delete=models.CASCADE,blank=True,null=True
	)
	#timestamp = models.ManyToManyField(TimestampStats)
	side = models.ForeignKey(
		Side,
		on_delete=models.CASCADE,
	)
	player = models.ForeignKey(
		Player,
		on_delete=models.CASCADE,
	)

	def __str__(self):
		return "stats of player {0} in {1}".format(self.player,self.side)


class Event(models.Model):
	EVENT_TYPE = [
	('BUILDING_KILL', 'BUILDING_KILL'),
	('CHAMPION_KILL', 'CHAMPION_KILL'),
	('ELITE_MONSTER_KILL', 'ELITE_MONSTER_KILL'),
	('ITEM_DESTROYED', 'ITEM_DESTROYED'),
	('ITEM_PURCHASED', 'ITEM_PURCHASED'),
	('ITEM_SOLD', 'ITEM_SOLD'),
	('ITEM_UNDO', 'ITEM_UNDO'),
	('SKILL_LEVEL_UP', 'SKILL_LEVEL_UP'),
	('WARD_KILL', 'WARD_KILL'),
	('WARD_PLACED', 'WARD_PLACED')
	]

	eventType = models.CharField(max_length = 30, choices = EVENT_TYPE)
	timestamp = models.PositiveIntegerField(blank=True,null=True)
	playerstat = models.ForeignKey(
		PlayerStats,
		on_delete=models.CASCADE,
		blank=True,null=True
	)


	####### ITEM Attribut

	gear = models.ForeignKey( Gear,
		on_delete=models.CASCADE,blank=True,null=True)

	###### Level Attribut 
	LEVEL_UP_TYPE = [
		('NORMAL','NORMAL'),
		('EVOLVE','EVOLVE'),

	]
	levelUpType = models.CharField(max_length = 30, choices = LEVEL_UP_TYPE,blank=True,null=True)
	skillSlot=  models.PositiveIntegerField(blank=True,null=True)

	##### Ward Attribut 
	WARD_TYPE = [
		('YELLOW_TRINKET','YELLOW_TRINKET'),
		('BLUE_TRINKET','BLUE_TRINKET'),
		('CONTROL_WARD','CONTROL_WARD'),
		('SIGHT_WARD','SIGHT_WARD'),
		('UNDEFINED','UNDEFINED'),
	]	
	wardType = models.CharField(max_length = 30, choices = WARD_TYPE,blank=True,null=True)

	#### Building Attribut 
	BUILDING_TYPE = [
		('TOWER_BUILDING','TOWER_BUILDING'),
		('INHIBITOR_BUILDING','INHIBITOR_BUILDING'),
	]

	LANE_TYPE = [
		('MID_LANE','MID_LANE'),
		('BOT_LANE','BOT_LANE'),
		('TOP_LANE','TOP_LANE'),

	]
	TOWER_TYPE = [
		('NEXUS_TURRET','NEXUS_TURRET'),
		('INNER_TURRET','INNER_TURRET'),
		('OUTER_TURRET','OUTER_TURRET'),
		('BASE_TURRET','BASE_TURRET'),
		('UNDEFINED_TURRET','UNDEFINED_TURRET'),
	]
	buildingType = models.CharField(max_length = 30, choices = BUILDING_TYPE,blank=True,null=True)
	laneType = models.CharField(max_length = 30, choices = LANE_TYPE,blank=True,null=True)
	towerType= models.CharField(max_length = 30, choices = TOWER_TYPE,blank=True,null=True)
	side = models.ForeignKey(
		Side,
		on_delete=models.CASCADE,
		blank=True,null=True
	)

	#### Monster Attribut 
	MONSTER_TYPE = [
		('BARON_NASHOR','BARON_NASHOR'),
		('RIFTHERALD','RIFTHERALD'),
		('DRAGON','DRAGON'),

	]
	MONSTER_SUB_TYPE = [
		('FIRE_DRAGON','FIRE_DRAGON'),
		('WATER_DRAGON','WATER_DRAGON'),
	]
	monsterSubType= models.CharField(max_length = 30, choices = MONSTER_SUB_TYPE,blank=True,null=True)
	monsterType= models.CharField(max_length = 30, choices = MONSTER_TYPE,blank=True,null=True)


	#### Champion Killed Attribut
	assistingParticipants = models.ManyToManyField(PlayerStats,
		related_name='assistEvents')
	victim = models.ForeignKey(
		PlayerStats,
		on_delete=models.CASCADE,
		blank=True,null=True,
		related_name='deathEvents'
	)
	

	class Meta:
		unique_together = (('playerstat', 'timestamp','eventType'),)

	def __str__(self):
		return "Event Type {0} of {1}".format(self.eventType,self.playerstat)

	def UpdateEvent(self,event):
		ev = self
		ev_type = event['type']
		if 	ev_type == 'BUILDING_KILL':
			self.buildingType = event['buildingType']
			self.laneType = event['laneType']
			self.towerType = event['towerType']
		elif 'ITEM_UNDO' in ev_type:
			item_id = event.get('afterId') if event.get('afterId') != 0 else event.get('beforeId') 
			try:
				self.gear = Gear.objects.get(gearId=item_id )
			except Exception as e:
				pprint(event)
				raise e
		elif 'ITEM' in ev_type:
			try:
				self.gear = Gear.objects.get(gearId=event['itemId'] )
			except Exception as e:
				pprint(event)
				raise e
		elif ev_type == 'ELITE_MONSTER_KILL':
			self.monsterType = event['monsterType']
			self.monsterSubType = event.get('monsterSubType')
		elif 'WARD' in ev_type:
			self.wardType = event['wardType']
		elif ev_type == 'SKILL_LEVEL_UP':
			self.skillSlot = event['skillSlot']
			self.levelUpType = event['levelUpType']
	
class TimestampStats(models.Model):
	timestamp = models.PositiveIntegerField(blank=True,null=True)
	playerstat = models.ForeignKey(
		PlayerStats,
		on_delete=models.CASCADE,
	)
	currentGold = models.IntegerField(blank=True,null=True)
	totalGold = models.IntegerField(blank=True,null=True)
	level = models.IntegerField(blank=True,null=True)
	xp = models.IntegerField(blank=True,null=True)
	minionsKilled = models.IntegerField(blank=True,null=True)
	jungleMinionsKilled = models.IntegerField(blank=True,null=True)
	dominionScore = models.IntegerField(blank=True,null=True)

	class Meta:
		unique_together = (('playerstat', 'timestamp'),)

	def __str__(self):
		return "Time {1} stats of {0}".format(self.playerstat,self.timestamp)
