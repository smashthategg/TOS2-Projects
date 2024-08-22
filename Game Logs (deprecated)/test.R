setwd("C:/Users/jzlin/OneDrive/Documents/TOWN OF SALEM 2")

games <- read.csv("./tos_ranked - game_logs.csv")


ti_roles <- c("Coroner","Investigator","Lookout","Psychic","Seer","Sheriff","Spy","Tracker")
tp_roles <- c("Bodyguard","Cleric","Crusader","Trapper")
tpow_roles <- c("Jailor","Mayor","Monarch","Prosecutor")
tk_roles <- c("Deputy","Trickster","Veteran","Vigilante")
ts_roles <- c("Admirer","Amnesiac","Retributionist","Tavern Keeper")
town_roles <- c(ti_roles,tp_roles,tk_roles,ts_roles,tpow_roles)

cd_roles <- c("Dreamweaver","Enchanter","Illusionist","Medusa")
ck_roles <- c("Conjurer","Jinx","Ritualist")
cpow_roles <- c("Coven Leader","Hex Master","Witch")
cu_roles <- c("Necromancer","Poisoner","Potion Master","Voodoo Master","Wildling")
cov_roles <- c(cd_roles,ck_roles,cpow_roles,cu_roles)

na_roles <- c("Baker","Berserker","Plaguebearer","Soul Collector")
nk_roles <- c("Arsonist","Serial Killer","Shroud","Werewolf")
ne_roles <- c("Doomsayer","Executioner","Jester")
neut_roles <- c(na_roles,nk_roles,ne_roles)

total_games <- nrow(games)
total_wins <- sum(games$WINLOSS == "W")
total_wr <- total_wins/total_games

total_town_games <- sum(games$ROLE%in%town_roles)
total_town_wins <- sum(games$ROLE%in%town_roles & games$WINLOSS == "W")
town_wr <- total_town_wins/total_town_games

total_cov_games <- sum(games$ROLE%in%cov_roles)
total_cov_wins <- sum(games$ROLE%in%cov_roles & games$WINLOSS == "W")
cov_wr <- total_cov_wins/total_cov_games

total_neut_games <- sum(games$ROLE%in%neut_roles)
total_neut_wins <- sum(games$ROLE%in%neut_roles & games$WINLOSS == "W")
neut_wr <- total_neut_wins/total_neut_games

total_elo_gained <- tail(games$ELO,1) - head(games$ELO,1)
avg_elo_gained <- total_elo_gained/nrow(games)

barplot(c(town_wr,cov_wr,neut_wr,total_wr),
        main="Ranked Winrate by Faction",xlab="Faction",ylab="Winrate",
        names=c("Town","Coven","Neutral","All Roles"),col = c("green","purple","gray","yellow"))

plot(games$ELO,type="p")
qqnorm(games$ELO)
qqline(games$ELO)
