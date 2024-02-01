//Greeting
console.log('plz don\'t try to break my game. Thanks 🙏!')

//CONSTANTS 
const BOARD_DIM = 11;

//Initialize primary variables
const game = data.game;
const player = data.user;
const players = data.players;
let board = data.board_rep;
const cardDirs =  [(idxs) => {return [idxs[0]-1, idxs[1]]}, (idxs) => {return [idxs[0]+1, idxs[1]]}, 
(idxs) => {return [idxs[0], idxs[1]-1]}, (idxs) => {return [idxs[0], idxs[1]+1]}];
let selectObj;

//HELPERS
const calcIndices = (num) => {
    return [Math.floor(num/BOARD_DIM), num % BOARD_DIM];
}

const calcIndex = (nums) => {
    return nums[0]*BOARD_DIM + nums[1];
}

const locate = (tile) => {
    let id = tile.id;
    for (let i=0; i<tiles.length; i++) {
        let currTile = tiles[i];
        if (currTile.id == id) {
            return i;
        }
    }
}

const validIndices = (nums) => {
    return !(nums[0] == -1 || nums[0] == BOARD_DIM || nums[1] == -1 || nums[1] == BOARD_DIM);
}

const sameSide = (piece) => {
    let pcside = piece.classList[1];
    return (pcside == playerSide || (pcside == 'king' && playerSide == 'defender'))
}

const findPT = (targ) => {
    let tile;
    let piece;
    if (targ.classList[0] == 'piece') {
        piece = targ;
        tile = piece.parentNode;
    } else {
        tile = targ;
        piece = tile.children[0];
    }
    return [piece, tile];
}

const mapToNum = (cls) => {
    switch (cls) {
        case ('invader'): return "1"
        case ('defender'): return "2"
        case ('king'): return "3"
    }
}

const sendData = async (content) => {
    content.gid = game.id;
    let options = {
        method : 'POST',
        headers : {
            'Content-Type': 'application/json',
        },
        body : JSON.stringify(content)
    };
    return fetch(location.origin + '/move', options).then((reply) => {
        if (!reply.ok) {throw Error(reply.status);}
        else {return reply.json()}
    }).then((data => {
        return data;
    })).catch(err => {
        console.log(err);
        return false;
    });
}

const triSurrounded = (idcs) => {
    let cnt = 0;
    cardDirs.forEach((dir) => {
        let adjIdcs = dir(idcs);
        if (validIndices(idcs) && board[adjIdcs[0]][adjIdcs[1]] == '1') {
            cnt++;
        }
    })
    return cnt == 3;
}

const findCaptures = (tile) => {
    let idcs = calcIndices(locate(tile));
    let playerNums = (playerSide == 'invader' ? ['1'] : ['2', '3']);
    let captures = [];
    cardDirs.forEach((dir) => {
        let adjIdcs = dir(idcs);
        if (validIndices(adjIdcs)) {
            let adjNum = board[adjIdcs[0]][adjIdcs[1]];
            if (!playerNums.includes(adjNum) && adjNum != '0') {
                if (adjNum == 3) {
                    if (triSurrounded(adjIdcs)) {
                        captures.push(tiles[calcIndex(adjIdcs)]);
                    }
                } else {
                    let nextIdcs = dir(adjIdcs);
                    if (validIndices(nextIdcs)) {
                        let nextNum = board[nextIdcs[0]][nextIdcs[1]];
                        let nextTile = tiles[calcIndex(nextIdcs)];
                        if (playerNums.includes(nextNum) || (nextTile.classList[1] == 'spec_tile' && nextTile.children.length == 0)) {
                            captures.push(tiles[calcIndex(adjIdcs)]);
                        }
                    }
                }
            }
        }
    });
    return captures;
}

const triggerSound = (sound) => {
    if (window.localStorage.getItem('sfx') == 'on') {
        let audioEl = document.querySelector(`audio[src*="${sound}"]`);
        audioEl.play().catch((e) => {
            console.log('Sound failed to play because of autoplay policy. Enable autoplay for a better experience.');
        });
    }
}

//Initialize secondary variables
let tiles;
const refreshTiles = () => {tiles = Array.from(document.getElementsByClassName('tile'));}
refreshTiles()
const playerSide = (game.turn == game.king ? 'defender' : 'invader');
const candidateTiles = tiles.filter((tl) => {return tl.children.length == 1 && sameSide(tl.children[0]);});

//Sidebar functionality
const toggleAbs = (name, val1, val2, endAction) => {
    return () => {
        window.localStorage.setItem(name, (window.localStorage.getItem(name) == val1 ? val2 : val1));
        triggerSound('Click');
        if (endAction) {
            endAction()
        }
    }
}

const implementRefresh = () => {
    if (!(player.id == players[game.turn].id) && !(window.localStorage.getItem('no_refresh') == 'true')) {
        setTimeout(()=>{location.reload()}, 5000);
    } 
}

$('#controls img').on('click', toggleAbs('sfx', 'off', 'on', toggleSFX));
$('#size_toggle').on('click', toggleAbs('size', 'big', 'small', toggleSize));
$('#refresh_toggle').on('click', toggleAbs('no_refresh', 'true', 'false', () => {
    toggleRefresh();
    implementRefresh();
}));

//Game functionality
const preview = (e) => {
    let tile = e.target;
    tile.style.outline = '5px solid var(--spec-border)';
    tile.style.zIndex = '1';
    let caps = selectObj.capObj[tile.id];
    caps.forEach((tl) => {
        let blackDot = document.createElement('div');
        blackDot.classList.add('black_dot');
        let pc = tl.children[0];
        pc.appendChild(blackDot);
    });
    tile.addEventListener('mouseout', remPreview);
}

const remPreview = (e) => {
    let tile = e.target;
    tile.style.outline = '3px solid var(--spec-border)';
    tile.style.zIndex = '';
    let caps = selectObj.capObj[tile.id];
    caps.forEach((tl) => {
        let pc = tl.children[0];
        pc.removeChild(pc.children[0]);
    });
    tile.removeEventListener('mouseout', remPreview);
} 

const move = async (e) => {
    let tile = e.target;
    let toIdcs = calcIndices(locate(tile));
    let fromIdcs = calcIndices(locate(selectObj.tile));
    let numType = mapToNum(selectObj.piece.classList[1]);
    let caps = selectObj.capObj[tile.id];
    let capNumLocs = caps.map((cap) => {return [mapToNum(cap.children[0].classList[1]), calcIndices(locate(cap))];});

    let content = {
        move : {
            type : numType,
            start : fromIdcs,
            end : toIdcs,
            caps : capNumLocs
        }
    }
    let resp = await sendData(content);
    if (resp == 'success') {
        remPreview(e);
        reset();
        await animateMove(content.move);
        location.reload();
    } else {
        popup(resp);
    }
}

const select = (piece, tile) => {
    let idx = locate(tile);
    let indices = calcIndices(idx);

    const availableIndices = (nextIdxs) => {
        const innerAvailableIndices = (idxs) => {
            if (idxs[0] == -1 || idxs[0] == BOARD_DIM || idxs[1] == -1 || idxs[1] == BOARD_DIM) {
                return [];
            } else {
                let tileVal = board[idxs[0]][idxs[1]]
                if (tileVal != 0) {
                    return [];
                } else {
                    let currIdcs = innerAvailableIndices(nextIdxs(idxs))
                    currIdcs.unshift(idxs)
                    return currIdcs;
                }
            }
        }
        return innerAvailableIndices(nextIdxs(indices));
    }
    let avIdxs = cardDirs.reduce((cum, dir)=>{return cum.concat(availableIndices(dir))}, []);
    
    reset();
    tile.setAttribute("data-selected", true);
    selectObj = {
        piece : piece,
        tile : tile,
        choices : [],
        capObj : {}
    };
    if (avIdxs.length > 0) {
        avIdxs.forEach((idxs) => {
            let htmlIdx = calcIndex(idxs);
            let currTile = tiles[htmlIdx];
            if (!(currTile.classList[1] == 'spec_tile' && !(piece.classList[1] == 'king' && playerSide == 'defender'))) {
                currTile.style.outline = '3px solid var(--spec-border)';
                currTile.style.backgroundColor = 'var(--spec-fill)';
                currTile.addEventListener('click', move);
                currTile.addEventListener('mouseover', preview);
                selectObj.choices.push(currTile);
                selectObj.capObj[currTile.id] = findCaptures(currTile);
            }
        });
    }
}

const reset = () => {
    tiles.forEach((tl) => {
        tl.style.outline = '';
        tl.style.backgroundColor = '';
    })
    if (selectObj) {
        selectObj.choices.forEach((tl)=>{
            tl.removeEventListener('click', move);
            tl.removeEventListener('mouseover', preview);
        });
        selectObj.tile.removeAttribute("data-selected");
    }
}

const manageSelect = (e) => {
    let [piece, tile] = findPT(e.target);
    if (tile.dataset.selected) {
        reset();
    } else {
        select(piece, tile);
    }
}

const gameOver = () => {
    let endScreen = document.createElement('div');
    endScreen.classList.add('end_screen')
    if (player.id == players[game.victor].id) {
        endScreen.id = 'end_win';
        endScreen.innerHTML = "<h1>You Win</h1>";
        triggerSound('Winner');
    } else {
        endScreen.id = 'end_lose';
        endScreen.innerHTML = "<h1>You Lose</h1>";
        triggerSound('Loser');
    }
    document.getElementById('game_board').appendChild(endScreen);

    let turnIndicator = document.getElementById('turn_indicator');
    turnIndicator.style.backgroundColor = 'transparent';
    turnIndicator.style.borderColor = 'var(--text)';
    turnIndicator.style.color = 'var(--text)';
    turnIndicator.innerHTML = 'GAME OVER';
}

const updateBoard = async (move) => {
    board[move.start[0]][move.start[1]] = '0';
    board[move.end[0]][move.end[1]] = move.type;
    let startTile = tiles[calcIndex(move.start)];
    let endTile = tiles[calcIndex(move.end)];
    let piece = startTile.children[0];
    piece.style = '';
    startTile.removeChild(piece);
    endTile.appendChild(piece);
    let fades = [];
    if (move.caps.length > 0) {
        console.log(move.caps)
        move.caps.forEach(async (pair) => {
            let idcs = pair[1]
            board[idcs[0]][idcs[1]] = '0';
            let currTile = tiles[calcIndex(idcs)];
            let currPiece = currTile.children[0];
            let prom = $(currPiece).fadeOut(1000).promise();
            fades.push(prom);
            prom.then(() => {currTile.removeChild(currPiece);})
        });
        triggerSound('Capture');
        await Promise.all(fades);
    }
    refreshTiles();
}  

const animateMove = async (move) => {
    let tile = tiles[calcIndex(move.start)];
    let tileDim = parseFloat(window.getComputedStyle(tile).getPropertyValue('width'));
    let pieceDim = tileDim * 3/4;
    let $piece = $(tile.children[0]);
    let mods = {
        width : `${pieceDim}px`,
        height : `${pieceDim}px`,
        position : 'absolute',
    }
    $piece.css(mods)
    let pad = tileDim * 0.125;
    movement = {
        top : `${move.end[0] * (tileDim + 3) + 5 + pad}px`,
        left : `${move.end[1] * (tileDim + 3) + 5 + pad}px`
    }
    let animateProm = $piece.animate(movement, 1000).promise();
    triggerSound('Move');
    await animateProm;
    await updateBoard(move);
}

const main = async () => {
    if (player.id == players[game.turn].id && game.last_move) {
        await animateMove(game.last_move);
    }
    if (game.victor != null) {
        gameOver()
    } else if (player.id == players[game.turn].id) {
        candidateTiles.forEach((tl)=>{tl.addEventListener('click', manageSelect);});
    } else {
        implementRefresh();
    }
}

main();